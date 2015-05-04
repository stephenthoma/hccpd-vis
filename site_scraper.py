import httplib2
import re
from HTMLParser import HTMLParser
from oauth2client.client import flow_from_clientsecrets

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

def main():
    http = do_ouath()
    req_url = 'https://sites.google.com/feeds/content/site/hccpdforum'
    all_content = ''
    content = http.request(req_url, 'GET')

    rexpr = r"<link rel='next' type='application/atom\+xml' href='https://sites\.google\.com/feeds/content/site/hccpdforum(\?start-index=\d{1,3})'/>"
    match = re.findall(rexpr, content[1])
    while match:
        all_content += content[1]
        content = http.request(''.join((req_url, match[0])), 'GET')
        match = re.findall(rexpr, content[1])
    processed_pages = process_pages(all_content)
    return processed_pages

if __name__ == "__main__":
    import pickle
    pgs = main()
    pickle.dump( pgs, open( "scraped_updates.p", "wb" ) )
