
import requests, requests.auth, pprint, time, re, bs4, os, getpass, argparse
import send2trash

from pathlib import Path

DownloadRetries = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    }

# BUG
# A certain furaffinity url fails getting a filename url
# Reddit's dumb overlay keeps breaking downloads 

# BUG
# https://www.reddit.com/gallery/139m7kz
# mediaUrl: str = media['s']['u'].replace("preview", "i")
# KeyError: 'u'

class User():
    username: str
    password: str
    appUsername: str
    appPassword: str

    def __init__(self, username: str, password: str, appUsername: str, appPassword: str):
        self.username = username
        self.password = password
        self.appUsername = appUsername
        self.appPassword = appPassword
    def __getitem__(self, item):
        return getattr(self, item)



class Environment():
    user: User
    customFeedName: str
    downloadFromSpecificSite: str # boolean
    specificSiteName: list[str] = []


    def __init__(self, user: User, customFeedName: str, downloadFromSpecificSite: str, specificSiteName: str):
        self.user = user
        self.customFeedName = customFeedName
        self.downloadFromSpecificSite = downloadFromSpecificSite

        if ',' in specificSiteName:
            specificSiteName = specificSiteName.split(',')
            self.specificSiteName.extend(specificSiteName)
        else:
            self.specificSiteName.append(specificSiteName)
    
    def __getitem__(self, item):
        return getattr(self, item)


def log(message, signal = None, prettyprint = False):
    if prettyprint:
        pprint.pprint(message)
    else:
        print(message)
        
    
    if signal:
        if prettyprint:
            message = pprint.pformat(message)
        signal.emit(str(message))


def getRedgifIDFromUrl(url: str):

    redgifIDRegex = re.compile(r'\w+\/\w+\/(\w+)(\.\w+)*')

    matchRedgifURL = redgifIDRegex.search(url)

    redgifID = matchRedgifURL.group(1)
    
    return redgifID

def getFilenameFromURL(url: str, type: str = None):

    urlFilenameRegex = re.compile(r'[a-zA-Z0-9]\/([A-Za-z0-9-]+\.?([-a-zA-Z0-9_]+)?(\.[a-zA-Z]+[0-9]*))\??([a-zA-Z0-9&]+)*\b')

    matchFilenameFromURL = urlFilenameRegex.search(url)

    if type == "furaffinity":
        filename = f"{matchFilenameFromURL.group(2)}{matchFilenameFromURL.group(3)}"
    else:
        filename = matchFilenameFromURL.group(1)

    return filename

def getCredentials(environment: Environment):

    if environment["user"]["username"]:
        username = environment["user"]["username"]
    else:
        username = input("Please provide your reddit profile username: ")
    
    if environment["user"]["password"]:
        password = environment["user"]["password"]
    else:
        password = getpass.getpass("Please provide your reddit profile password: ")

    if environment["user"]["appUsername"]:
        appUsername = environment["user"]["appUsername"]
    else:
        appUsername = input("Please provide a reddit app username: ")
    
    if environment["user"]["appPassword"]:
        appPassword = environment["user"]["appPassword"]
    else:
        appPassword = getpass.getpass("Please provide a reddit app password: ")

    return User(username, password, appUsername, appPassword)

def getEnvironment():
    redditUsername = os.environ.get("REDDIT_USERNAME")
    redditPassword = os.environ.get("REDDIT_PASSWORD")
    redditAppUsername = os.environ.get("REDDIT_APP_USERNAME")
    redditAppPassword = os.environ.get("REDDIT_APP_PASSWORD")

    redditUser = User(redditUsername, redditPassword, redditAppUsername, redditAppPassword)

    customFeed = os.environ.get("REDDIT_CUSTOM_FEED_NAME")

    downloadFromSpecificSite = os.environ.get("REDDIT_DOWNLOAD_ONLY_CONTENT_FROM_SPECIFIC_SITE")

    specificSiteName = os.environ.get("REDDIT_SPECIFIC_SITE")

    return Environment(redditUser, customFeed, downloadFromSpecificSite, specificSiteName)

def getRedditAccessToken(user):

    auth = requests.auth.HTTPBasicAuth(user["appUsername"], user["appPassword"]) # In "developed applications": Username = the hash under the App name, Password = secret when you click edit on the reddit app

    data = { 'grant_type': 'password',
            'username': user["username"],
            'password': user["password"] }
    
    headers= {'User-Agent': 'Lilscrapy/0.0.1'}

    accessTokenResponse = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers,
                        params={'limit': '100'})
    
    token = accessTokenResponse.json()['access_token']

    return token

def getRedgifsTemporaryToken():

    redgifsTokenResponse = requests.get("https://api.redgifs.com/v2/auth/temporary", headers=HEADERS)
    redgifsTokenResponse.raise_for_status()

    return redgifsTokenResponse.json()["token"]

def getRedgifsContentLinkFromApi(token, id, msgSignal, headers):

    redgifApiResponse = requests.get(f"https://api.redgifs.com/v2/gifs/{id}", headers=headers)
    redgifApiResponseLog = f"Api Response: {redgifApiResponse.text}"
    log(redgifApiResponseLog, msgSignal)

    return redgifApiResponse.json()["gif"]["urls"]["hd"]


def getPostsPaginated(lastItem: str, headers: dict, user: User, customFeed: str):

    if not lastItem:
        redditPostResponse = requests.get(f'https://oauth.reddit.com/user/{user["username"]}/m/{customFeed}/', headers=headers,
                params={'limit': '100'})
    else:
        redditPostResponse = requests.get(f'https://oauth.reddit.com/user/{user["username"]}/m/{customFeed}/', headers=headers,
                        params={'limit': '100', 'after': lastItem})
    
    redditPostResponse.raise_for_status()

    return redditPostResponse.json()['data']['children']

def ceaseSpamming(postsSpammedSoFar, msgSignal):
    if postsSpammedSoFar % 3 == 1:
        log("Ceasing spamming for 5 seconds", msgSignal)
        time.sleep(5)

def downloadContent(fileName, contentResponse, matchSite, unsupportedSiteUrls, postUrl, path, mediaSignal, msgSignal):
    try:

        downloadLog = f"Downloading {fileName}"
        log(downloadLog, msgSignal)
        
        download = open(os.path.join(f'{path}/Content to be filtered','Reddit', fileName), 'wb')

        megabyteInBytes = (1024*1024)

        chunkProgress = 0
        chunkTotal = int(contentResponse.headers['content-length'])
        chunkTotalInMB = round(chunkTotal/megabyteInBytes, 2)

        contentIteration = 1000000

        for chunk in contentResponse.iter_content(contentIteration):
            
            chunkSize = len(chunk)
            chunkSizeInMB = round(chunkSize/megabyteInBytes, 2)
            chunkProgress += chunkSizeInMB

            try:
                chunkPercentage = round(chunkProgress/chunkTotalInMB * 100, 2)

                chunkLog = f"{chunkPercentage}%"
                log(chunkLog, msgSignal)

                if mediaSignal:
                    mediaSignal.emit(chunkPercentage + 1)

            except ZeroDivisionError:
                log("Doesn't exist anymore", msgSignal)

            download.write(chunk)
        download.close()
    except Exception as e:
        log(f"Exception {e}", msgSignal)

        if 'content-length' in str(e) and (matchSite.group() in ["i.redd.it", "reddit"]):
            log(f"Reddit overlay error", msgSignal)
        else:
            log(f"'content-length' in {str(e)}", msgSignal)
            time.sleep(60) # give time for exception reading
        
        download.close()

        filePath = Path(f"{path}\\Content to be filtered\\Reddit\\{fileName}")

        send2trash.send2trash(filePath) # delete failed download file

        unsupportedSiteUrls.append(postUrl)

def getRawContent(contentLink, msgSignal):
    retryAttempts = 0

    okResponse = False

    contentHeaders = {**HEADERS, **{"Accept": "image/*, video/*",}}

    while okResponse == False:
        try:
            contentResponse = requests.get(contentLink, headers=contentHeaders)
            contentResponse.raise_for_status()
        except Exception as e:
            if retryAttempts < DownloadRetries:
                
                exceptionTitleLog = f"Connection exception: Trying again {contentLink}"
                log(exceptionTitleLog, msgSignal)

                exceptionAttemptLog = f"Attempt: {str(retryAttempts + 1)}"
                log(exceptionAttemptLog, msgSignal)

                
                log(e, msgSignal)

                retryAttempts += 1
            else:

                log("Failed to get content response", msgSignal)
                log(e, msgSignal)

                return None

        okResponse = contentResponse.status_code == 200
    
    return contentResponse


def main(pages, customFeed = None, destinationPath = None, msgSignal = None, clsSignal = None, mediaSignal = None, overallSignal = None, allStages = None, currentStage = None):

    os.makedirs(os.path.join(f'{destinationPath}/Content to be filtered',"Reddit"), exist_ok=True)

    siteRegex = re.compile(r'redgifs|imgur|i.redd.it|reddit|patreon|hentai-foundry|youtu.be|furaffinity|gfycat|e621|catbox')

    unsupportedSiteUrls = []
    failedFileNames = []

    env: Environment = getEnvironment()

    user: User = getCredentials(env)
    if not customFeed and env["customFeedName"]:
        customFeed = env["customFeedName"]

    if not customFeed:
        customFeed = input("Provide custom feed name to download from: ")

    redditToken = getRedditAccessToken(user)
    headers = {**HEADERS, **{'Authorization': f"bearer {redditToken}"}}

    lastPostOnPreviousPage = None
    for paginationPage in range(1, pages + 1):
        posts = getPostsPaginated(lastPostOnPreviousPage, headers, user, customFeed) 

        currentPostNumber = 1
        for post in posts:

            postUrl: str = post['data']['url']
            postTitle = str(currentPostNumber) + "-" + str(paginationPage) + " " + postUrl
            log(postTitle, msgSignal)

            ceaseSpamming(currentPostNumber, msgSignal)

            matchSite = siteRegex.search(postUrl)

            fileName = ""
            contentResponse = None
            filenames = []
            contentResponses = []
            if matchSite:
                
                skipPost = env["downloadFromSpecificSite"] == "True" and matchSite.group() not in env["specificSiteName"]

                if skipPost:
                    currentPostNumber += 1
                    continue

                postSite = matchSite.group()
                postSiteLog = "This link is for " + postSite
                log(postSiteLog, msgSignal)

                if matchSite.group() == "redgifs":
                    if matchSite.group().startswith("https://i.redgifs"):
                        print("redgifs image -- skipping")
                    else:
                        okResponse = False
                        attempts = 0

                        redgifsToken = getRedgifsTemporaryToken()
                        
                        while okResponse == False:
                            if attempts >= DownloadRetries: 
                                log("Attempts: " + str(attempts +1), msgSignal)
                                unsupportedSiteUrls.append(link)
                                break
                            
                            log("Finding link in redgifs.", msgSignal)

                            redgifId = getRedgifIDFromUrl(postUrl)

                            redgifHeaders = {
                                **HEADERS,
                                **{"Authorization": f"Bearer {redgifsToken}"},
                                }


                            link = getRedgifsContentLinkFromApi(redgifsToken, redgifId, msgSignal, redgifHeaders)
                                
                            log("Link: ", msgSignal)
                            log(link, msgSignal)
                            
                            try:
                                contentResponse = requests.get(link, headers=redgifHeaders)
                                contentResponse.raise_for_status()
                            except Exception as e:
                                log(e, msgSignal)
                                log("Trying again", msgSignal)
                                attempts += 1

                            if attempts >= 3: time.sleep(60)

                            okResponse = contentResponse.status_code == 200
                            
                            fileName = getFilenameFromURL(link)

                            log(fileName, msgSignal)

                elif matchSite.group() == "i.redd.it" or matchSite.group() == "e621" or matchSite.group() == "furaffinity" or matchSite.group() == "catbox":

                    fileName = getFilenameFromURL(postUrl, matchSite.group())

                    redditHeaders = {**HEADERS, **{"Accept": "image/*, video/*",}}

                    contentResponse = requests.get(postUrl, headers=redditHeaders)
                    

                elif matchSite.group() == "reddit":
                    if "gallery" in postUrl:
                        try:
                            galleryMedia = post["data"]["media_metadata"]
                        except KeyError as e:
                            if 'media_metadata' in str(e):
                                log("Reddit being wank", msgSignal)
                                unsupportedSiteUrls.append(postUrl)
                                galleryMedia = []
                        contentLinks = []
                        for mediaName in galleryMedia:
                            media = galleryMedia[mediaName]
                            if media["status"] != "failed":
                                mediaUrl: str = media['s']['u'].replace("preview", "i")
                                contentLinks.append(mediaUrl)
                                filenames.append(getFilenameFromURL(mediaUrl))

                        log("Gallery found!", msgSignal)

                        for link in contentLinks:
                            contentResponse = getRawContent(link, msgSignal)
                            if contentResponse:
                                contentResponses.append(contentResponse)
                    else:
                        log("???", msgSignal)

                        unsupportedSiteUrls.append(postUrl)


                elif matchSite.group() == "imgur":
                    if postUrl.endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4')):
                        fileName = getFilenameFromURL(postUrl)
                        contentLink = postUrl
                    
                    if postUrl.endswith('.gifv'):
                        contentLink = postUrl.replace(".gifv", ".mp4")

                        if contentLink:
                            log(contentLink, msgSignal)

                            fileName = getFilenameFromURL(contentLink)
                    
                    contentResponse = getRawContent(contentLink, msgSignal)
                    
                else:
                    log("------------------------------Unsupported site", msgSignal)
                    unsupportedSiteUrls.append(postUrl)

                    

                if fileName != "" and contentResponse != None:   
                    downloadContent(fileName, contentResponse, matchSite, unsupportedSiteUrls, postUrl, destinationPath, mediaSignal, msgSignal)
                if len(filenames) > 0 and len(contentResponses) > 0:
                    for i, response in enumerate(contentResponses):
                        downloadContent(filenames[i], response, matchSite, unsupportedSiteUrls, postUrl, destinationPath, mediaSignal, msgSignal)

            currentPostNumber += 1
            if post == posts[-1]:
                lastPostOnPreviousPage = post['kind'] + '_' + post['data']['id']

                log(lastPostOnPreviousPage, msgSignal)

            os.system('cls')
            if clsSignal: clsSignal.emit("")

        if overallSignal:
            currentStage += 1
            overallSignal.emit((currentStage/allStages)*100)

    # TODO: Add different text if no unsupported urls were found
    log("Unsupported site urls:" + '\n - ' + '\n - '.join(unsupportedSiteUrls), msgSignal)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pagesToDownload', dest='pagesToDownload', type=int, help="Pages for the scraper to download", required=True)
    parser.add_argument("--customFeedName", dest="customFeed", type=str, help="Custom feed name to scrape from")
    args = parser.parse_args()
    if args.customFeed:
        main(args.pagesToDownload, args.customFeed)
    else:
        main(args.pagesToDownload)