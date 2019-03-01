# Selenium

Based on the drivers of Firefox and Chrome, including headless, spider can collect data from target websites on different os.

## Project 1. Trademark

#### Target: 
1) collect all trademarks' info, including image and text, of specific companies from official website: http://wsjs.saic.gov.cn
2) reduce image size, to fit excel
3) parse all infos into a excel for relevent colleague


#### Challenge:
1) Website defence: multiple detection, including visiting frequency, mouse moving, click sequence, how to page down and page turn, and so on...
		if suspected, the website will delay server's response from several seconds to nearly a minute
		if detected, this ip will be banned
2) Downloading images failed: as earlier mentioned, if suspected, the website will take some actions. Image loading failed is one of them.
		Fortunately, my spider will record image url while recording other infos. After collecting all infos, the programming would retry downing by requests. 


#### Highlights:
1) Automation: the programming will deal all situations by itself, including all kinds of Exceptions
2) Headless: Debug in normal mode, and fix it in headless mode, which would be feasible for all Operation System
3) Attack: use random time, random seq, random mouse moving, and set random number of target for one browser 
4) Protect source images: before retrying download images which have been failed loading and reducing images size, the programming would save a copy for source images. 
5) Generating Excel Format: try to generate a beautiful excel for colleague


#### File Illustrate:
1) trademark.py : main(), has integrated other py files
2) deal_images.py : small function, for those images failed to download, retry to download images
3) image_reduce.py : small function, to reduce size of all images that under a specific folder 
4) get_excel.py : small function, use xlsx to generate excel
5) "财新传媒有限公司_2019-01-20.xlsx": Sample Results



## Project 2. Investors in V-Next

#### Target: 
1) collect all investor details, including image and text, on: https://www.v-next.cn/sizeContacts/list.do


#### Challenge:
1) Login: to visit each investor details, sign in is needed.


#### Highlights:
1) Login: firstly visit login page: https://www.v-next.cn/log/login.do
	  secondly, redirection details page and collect data.


#### File Illustrate:
1) Vnext.py: main()
2) Investor_Info.csv: Sample Results
3) folder image: icon




