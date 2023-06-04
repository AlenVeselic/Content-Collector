import requests, sys, bs4, shelve, re, ast, os, time, datetime, calendar, math, argparse, pprint, send2trash
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry
from .redditScraper import main as redditDownload
    
redditPages = 2

retryLimit = 10

# TODO: Add option to download only specific tag from list
# TODO: Merge tag crawler

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

class Environment():
    skipBooru: str
    skipReddit:str
    useApi: str

    baseDomain: str
    baseDomainPostsEndpoint: str

    apiDomain: str
    apiPostsEndpoint: str

    def __init__(self, skipBooru, skipReddit, useApi, baseDomain, baseDomainPostsEndpoint, apiDomain, apiPostsEndpoint):
        self.skipBooru = skipBooru
        self.skipReddit = skipReddit
        self.useApi = useApi

        self.baseDomain = baseDomain
        self.baseDomainPostsEndpoint = baseDomainPostsEndpoint

        self.apiDomain = apiDomain
        self.apiPostsEndpoint = apiPostsEndpoint
    
    def __getitem__(self, item):
        return getattr(self, item)

def loadEnvironment():
    skipBooru = os.environ.get("SKIP_BOORU")
    skipReddit = os.environ.get("SKIP_REDDIT")

    useApi = os.environ.get("BOORU_USE_API")

    baseDomain = os.environ.get("BOORU_DOMAIN")
    baseDomainPostsEndpoint = os.environ.get("BOORU_POSTS_ENDPOINT")

    apiDomain = os.environ.get("BOORU_API_DOMAIN")
    apiPostsEndpoint = os.environ.get("BOORU_API_POSTS_ENDPOINT")

    return Environment(skipBooru, skipReddit, useApi, baseDomain, baseDomainPostsEndpoint, apiDomain, apiPostsEndpoint)

def log(message, signal = None, prettyprint = False):
    if prettyprint:
        pprint.pprint(message)
    else:
        print(message)
        
    
    if signal:
        if prettyprint:
            message = pprint.pformat(message)
        signal.emit(str(message))


def main(path, shelvePath: str = None, messageSignal = None, clsSignal = None, mediaSignal = None, overallSignal = None):

    environment: Environment = loadEnvironment()

    filteredContent = []

    os.makedirs(f'{path}/Content to be filtered', exist_ok = True)

    objectRegex = re.compile(r"{.+}", re.DOTALL)

    baseUrl = environment["baseDomain"]
    websiteEndpoint =environment["baseDomainPostsEndpoint"]

    apiUrl = environment["apiDomain"]
    apiEndpoint = environment["apiPostsEndpoint"]

    termInterval = 5
    postInterval = 5

    if shelvePath:
        data = shelve.open(shelvePath)
    else:
        data = shelve.open(f'{path}/Data/SmuttyData')
    try: 
        try:
            terms = data['terms']
        except Exception as e:
            log("Shelve data doesn't exist", messageSignal)
            
            sys.exit()  
    except KeyError:
        data['terms'] = []
        terms = data['terms']
    
    log(f"Shelve path: {f'{path}/Data/SmuttyData'} \n Tags: {terms}")

    destinationDirs = []
    if "destinationDir" in data.keys():
        destination = data["destinationDir"][0]
        if "destinationFolders" in data.keys():
                if len(data["destinationFolders"]) > 1:
                    for folder in data["destinationFolders"]:
                        destinationDirs.append(os.path.join(destination, folder)) 
                else:
                    destinationDirs.append(os.path.join(destination, data["destinationFolders"])) 
    if "destinationDirectories" in data.keys():
        destinationFolders = data["destinationDirectories"]

        for folder in destinationFolders:
            destinationDirs.append(folder)

    for directory in destinationDirs:
        for (root,dirs,files) in os.walk(directory, topdown=True):
            filteredContent.extend(files)
    
    data.close()

    def waitBeforeDownloading(postNumber):
        return postNumber % 5 == 0


    def isWithinDateRange(postDate, finalDate):
        return postDate > finalDate

    def getContentData(postSoup):
        scriptIndex = 1
        contentDataFound = False
        while not contentDataFound:
            try:
                contentLink = postSoup.select('.content script')[scriptIndex]
                
                contentMatch = objectRegex.search(contentLink.string)
            
                contentData = ast.literal_eval(contentMatch.group())

                contentDataFound = True

            except Exception as e:
                log(str(e) + "was thrown", messageSignal)

                scriptIndex += 1
                continue
        log("Content data found after " + str(scriptIndex) + " tries", messageSignal)

        return contentData

        """ except AttributeError: 
            contentLink = postSoup.select('.content script')[2]

            contentMatch = objectRegex.search(contentLink.string)

            imageDict = ast.literal_eval(contentMatch.group())
        except SyntaxError:
            contentLink = postSoup.select('.content script')[3]

            contentMatch = objectRegex.search(contentLink.string)

            imageDict = ast.literal_eval(contentMatch.group()) """

    def checkTerm(term, totalPostNumber):
        os.makedirs(f'{path}\\Content to be filtered\\{term}', exist_ok = True)

        if environment["useApi"] == "True":
            termUrl = apiUrl + apiEndpoint + term
        else:
            termUrl = baseUrl + websiteEndpoint + term
        res = requests.get(termUrl, headers=HEADERS)
        res.raise_for_status()
        
        if environment["useApi"] == "True":
            posts = res.json()
        else:
            landingSoup = bs4.BeautifulSoup(res.text, 'html.parser')

            posts = landingSoup.select('.thumb a')

        postNumber = checkPosts(posts, totalPostNumber)
        
        return postNumber
        
    def checkPost(post, postNumber, lastPost):
        if environment["useApi"] == "True":
            postUrl = post["file_url"]
            postDatetime = datetime.datetime.fromtimestamp(post["change"])
        else:
            postUrl = baseUrl + post.get('href')

            session = requests.Session()
            retry = Retry(connect=5, backoff_factor=1)
            adapter = HTTPAdapter(max_retries=retry)

            session.mount('http://', adapter)
            session.mount('https://', adapter)


            postResponse = session.get(postUrl, headers=HEADERS)
            postResponse.raise_for_status()

            postSoup = bs4.BeautifulSoup(postResponse.text, 'html.parser')

            postDatetime = getPostDate(postSoup)
        
        today = datetime.datetime.now()

        postStatus = {
            'isLast': False,
            'downloaded': False
            }

        try:
            yesterday = datetime.datetime(today.year, today.month, today.day - 1, 0, 0, 0)
        except ValueError as error:
            if str(error) == "day is out of range for month":
                yesterday = datetime.datetime(today.year, today.month - 1, calendar.monthrange(today.year, today.month - 1)[1], 0, 0, 0 )

        if isWithinDateRange(postDatetime, yesterday):
            log("Post date is within range", messageSignal)

            if environment["useApi"] == "True":
                filename = post["image"]
            else:
                contentData = getContentData(postSoup)
                filename = contentData['img']

            displayPostInfo(term, postNumber, filename, postDatetime)
            
            isNew = checkAllFilterFolders(filename)
            isInDestination = checkDestination(filename)
            if isNew == False or isInDestination:
                log("You already have this image.", messageSignal)

                return postStatus
            
            else:
                log("Downloading " + filename, messageSignal)

            
                postData = {
                    'term': term,
                    'postNumber': postNumber,
                    'date': postDatetime
                }

                if environment["useApi"] == "True":
                    downloadPost(postData, post)
                else:
                    downloadPost(postData, contentData)

                postStatus['downloaded'] = True
                if post == lastPost:
                    postStatus['isLast'] = True
                return postStatus     
                            
        else:
            postStatus['isLast'] = True
            return postStatus

    def checkPosts(posts, totalPostNumber):
        downloadedPostNumber = 0
        postNumber = 0

        for post in posts:
            if waitBeforeDownloading(postNumber):
                time.sleep(postInterval)

            os.system('cls')
            if clsSignal: clsSignal.emit("")
            postResponse = checkPost(post, postNumber, posts[-1])
            postNumber += 1
            if postResponse['downloaded'] == True: 
                downloadedPostNumber += 1
            if postResponse['isLast'] == True: 
                totalPostNumber = totalPostNumber + postNumber
                displayTermCompletionInfo(term, postNumber, downloadedPostNumber, totalPostNumber)
                break
        
        return postNumber
            

    def getPostDate(postSoup):
        postDateAndAuthorNode = postSoup.select("#stats ul li")[1].stripped_strings
        dateAndAuthorNodeDividedIntoStrings = []

        for part in postDateAndAuthorNode:
            dateAndAuthorNodeDividedIntoStrings.append(part)

        datePartIndex = 0
        datePrefixTextLength = 7

        postDateInString = dateAndAuthorNodeDividedIntoStrings[datePartIndex][datePrefixTextLength:].strip()
        return datetime.datetime.fromisoformat(postDateInString)


    def checkAllFilterFolders(file): 
        foundIn = []
        log("Checking for " + file + " in filtration", messageSignal)

        filterFolders = os.listdir(f"{path}\Content to be filtered")

        for folder in filterFolders:
            if file in os.listdir(f"{path}\Content to be filtered" + "\\" + folder.strip()):
                foundIn.append(folder)
        if len(foundIn) > 0:
            log("This image was found in: ", messageSignal)

            for foundFolder in foundIn:
                log(foundFolder, messageSignal)

            return False
        return True

    def checkDestination(file):
        if str(file) in filteredContent:
            log("File " + file + " exists in destination directory.", messageSignal)

            return True
        return False

    def downloadPost(postData, contentData):

        if environment["useApi"] == "True":
            contentUrl = contentData["file_url"]

            filename = contentData["image"]

        else:
            filename = contentData['img']

            contentUrl = contentData['domain'] + contentData['base_dir'] + '/' + str(contentData['dir']) + '/' + filename

        retryAttempts = 0

        contentResponse = requests.Response()
        contentResponse.status_code = 0

        while contentResponse.status_code == 0:
            try:
                contentResponse = requests.get(contentUrl, headers=HEADERS)
                contentResponse.raise_for_status()

                checkHeader = contentResponse.headers['content-length']
            except KeyError as e:
                 contentUrl = contentData['domain'] + '/' + contentData['base_dir'] + '/' + str(contentData['dir']) + '/' + filename
                 contentResponse.status_code = 0
            except Exception as e:
                if retryAttempts < retryLimit:

                    log(f"Connection exception: Trying again {contentUrl}", messageSignal)
                    log("Attempt: " + str(retryAttempts + 1), messageSignal)
                    retryAttempts += 1
                    log(Exception, messageSignal)
                else:
                    log("Retries exceeded", messageSignal)
                    log(Exception, messageSignal)
                    contentResponse.raise_for_status()

        folderName = postData['term'].strip()

        download = open(os.path.join(path, 'Content to be filtered', folderName, filename), 'wb')
        chunkProgress = 0
        chunkTotal = int(contentResponse.headers['content-length'])
        chunkTotalInMB = round(chunkTotal/(1024*1024), 2)
        downloadFailed = False
        try:
            for chunk in contentResponse.iter_content(1000000):
                os.system('cls')
                if clsSignal: clsSignal.emit("")

                chunkSizeInMB = round(len(chunk)/(1024*1024), 2)
                chunkProgress += chunkSizeInMB
                
                chunkPercentage = round(chunkProgress/chunkTotalInMB * 100, 2)

                displayPostInfo(postData['term'], postData['postNumber'], filename, postData['date'])
                displayProgressBar(chunkPercentage, chunkTotalInMB)

                download.write(chunk)
        except Exception as e:
            log(f"Exception thrown: {str(e)}", messageSignal)
            log(f"StackTrace: {str(e)}", messageSignal)
            downloadFailed = True
        download.close()
        if downloadFailed:
            filePath = Path(f"{path}\\Content to be filtered\\{folderName}\\{filename}")
            send2trash.send2trash(filePath)


    def displayPostInfo(term, postNumber, fileName, date):
        log(term, messageSignal)
        log("Post number " + str(postNumber + 1), messageSignal)
        log(fileName, messageSignal)
        log(date, messageSignal)
        
    def displayTermCompletionInfo(term, termPosts, downloadedPosts, totalPosts):
        os.system('cls')
        if clsSignal: clsSignal.emit("")

        log(term, messageSignal)
        log(str(termPosts) + " posts checked!", messageSignal)
        log(str(totalPosts) + " total posts checked!", messageSignal)
        log(str(downloadedPosts) + " new smut get!", messageSignal) 

        time.sleep(postInterval)

    def displayProgressBar(chunkPercentage, fileSize):
        log("Content size: " + str(fileSize) + "MB", messageSignal)
        log(str(chunkPercentage)+ r"% done", messageSignal)

        if mediaSignal: mediaSignal.emit(chunkPercentage + 1)

        progressBar = ''
        for i in range(99):
            if(i + 1 < math.floor(chunkPercentage)):
                progressBar += '|'
            else:
                progressBar += '.'

        log(progressBar, messageSignal)



    """ try:
        data = shelve.open(r'./Data/SmuttyData')
        pastDownloads = data['pastDownloads']
    except KeyError:
        pastDownloads = [] """

    log('Starting scheduled booru update', messageSignal) # display text while downloading the search result page

    totalPostNumber = 0
    progressStages = len(terms) + redditPages
    currentStage = 0

    for term in terms:
        if environment["skipBooru"] == "False":
            time.sleep(termInterval)
            postNumber = checkTerm(term, totalPostNumber)
            totalPostNumber += postNumber
        currentStage += 1
        if overallSignal: overallSignal.emit((currentStage/progressStages)*100)
        

    log("Starting Reddit download", messageSignal)
    redditDownload(redditPages, None, path, messageSignal, clsSignal, mediaSignal, overallSignal, progressStages, currentStage)
    log("Done", messageSignal)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--destinationDirectory', dest='destinationDirectory', type=str, help="Where to download the content to", required=True)

    args = parser.parse_args()

    main(args.destinationDirectory)

    


