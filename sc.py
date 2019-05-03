#! /usr/bin/python3
# coding: utf-8


import requests, re, json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

URL = 'https://soundcloud.com/choicescarf/azure-heart'

class Sound(object):
	
	def __init__(self, URL):
		
		self.URL = URL
		
	def get(self):
		self.getHTML()
		self.prepareDL()
		self.saveSound()
		self.setImage()
	
	def prepareDL(self):
		self.getsoundName()
		self.setClientID()
		self.setSoundID_and_SoundURL()
		
	def setClientID(self):
		self.getClientID_JS()
		self.getClientID()
		
	def setSoundID_and_SoundURL(self):
		self.getSoundID()
		self.getsoundURL()
	
	def setImage(self):
		self.getImage()
		self.settingImage()
	
	def getHTML(self):
		res = requests.get(self.URL)

		print('URL:{}  {}'.format(self.URL, res.status_code))
		if res.status_code == 200:
			self.soundHTML = res.text

	def getsoundURL(self):
		soundURL = 'http_mp3_128_url'
	
		url = 'https://api.soundcloud.com/i1/tracks/{}/streams'.format(self.SoundID)
		param = {'client_id':self.ClientID}
	
		res = requests.get(url, params=param)
		print('URL:{}  {}'.format(url, res.status_code))
	
		if res.status_code == 200:
			self.soundURL = json.loads(res.text)[soundURL]	

	def getClientID_JS(self):
		script_URL = 'https://a-v2.sndcdn.com/'
		pattern = r'window\.webpackManifest\s*=\s*(\{.+\});'

		webpackManifest = json.loads(re.search(pattern, self.soundHTML).group(1))
	
		self.ClientID_JS = script_URL + webpackManifest['2']
		
		res = requests.get(self.ClientID_JS)
		if res.status_code == 200:
			self.appjs = res.text
	
	def getClientID(self):
		pattern = r',\s*client_id:["\'](.+?)["\']\s*,'
	
		self.ClientID = re.search(pattern, self.appjs).group(1)
	
	def getSoundID(self):
		pattern = r'["\']soundcloud://sounds:([0-9]+)["\']'
	
		self.SoundID = re.search(pattern, self.soundHTML).group(1)
			
	def getsoundName(self):
		
		pattern = r'<meta\s*property=["\']og:title["\']\s*content=["\'](.+?)["\']>'
		
		result = re.search(pattern, self.soundHTML)
		if result:
			self.soundName = result.group(1)
		else:
			self.soundName = 'download'
			
	def saveSound(self):
	
		res = requests.get(self.soundURL)
		print('Getting Sound Response Status: {}'.format(res.status_code))
		if res.status_code == 200:
			with open('./{}.mp3'.format(self.soundName), 'wb') as f: f.write(res.content)
			print('save ok')
			
	def getImage(self):
		
		pattern = r'<meta\s*property=["\']og:image["\']\s*content=["\'](.+?)["\']>'
		
		result = re.search(pattern, self.soundHTML)
		if result:
			self.ImageURL = result.group(1)
			self.Image = self.rqIm()
			print('image get  ok')
		else:
			self.ImageURL = None
			self.Image = None
			
	def rqIm(self):
		
		res = requests.get(self.ImageURL)
		print('URL:{}  {}'.format(self.ImageURL, res.status_code))
		
		if res.status_code == 200:
			return res.content
		
	def settingImage(self):
		
		pattern = r'(jpg)$|(png)$'
		
		if self.Image is None:
			return
		
		mp3 = MP3('./{}.mp3'.format(self.soundName), ID3=ID3)
		ext = re.search(pattern, self.ImageURL).group(1)
		
		if ext == 'jpg':
			ext = 'jpeg'
		
		try:
			mp3.add_tags()
		except error:
			pass
		
		mp3.tags.add(
			APIC(
				encoding=3,
				mime='image/{}'.format(ext),
				type=3,
				desc='Cover',
				data=self.Image
			)
		)
		
		mp3.save()
		
if __name__ == '__main__':
	import sys
	a = sys.argv
	if len(a) > 1:
		for i in range(len(a)):
			if i == 0:
				continue
			Sound(a[i]).get()
	else:
		print('input url')
		pass
