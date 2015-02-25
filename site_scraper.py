import httplib2
from oauth2client.client import flow_from_clientsecrets
from HTMLParser import HTMLParser

class UpdateExtractor(HTMLParser):
    def __init__(self):
        self.reset()
        self.in_title = False
        self.last_tag = None
        self.curr_page = None
        self.fed = []
        self.pages = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
        self.last_tag = tag

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        print data
        if self.in_title and self.last_tag == 'title':
            self.curr_page = data
            self.pages[self.curr_page] = ''

        elif not self.in_title and self.curr_page:
            self.pages[self.curr_page] += data

    def get_data(self):
        for page_title in self.pages.keys():
            if not page_title.lower().find('update'):
                self.pages.pop(page_title)
        return self.pages

def process_pages(html):
    stri = UpdateExtractor()
    stri.feed(html)
    return stri.get_data()

def do_ouath():
    flow = flow_from_clientsecrets('./client_secrets.json',
                                   scope='https://sites.google.com/feeds/',
                                   redirect_uri='https://www.example.com/oauth2callback')

    auth_uri = flow.step1_get_authorize_url()
    print auth_uri
    code = raw_input('Enter code: ')
    credentials = flow.step2_exchange(code)

    http = httplib2.Http()
    return credentials.authorize(http)

if __name__ == "__main__":
    http = do_ouath()
    base_url = 'https://sites.google.com/feeds/content/site/hccpdforum'
    content = http.request(base_url, 'GET')
    processed_pages = process_pages(content[1])
    print processed_pages.keys()
    print processed_pages[processed_pages.keys()[1]]
