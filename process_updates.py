import pickle
import uuid
import re

class Processor(object):
    """
    A utility for processing the raw text data pulled from the HCCPD site.
    """
    def __init__(self, update_file):
        self.update_file = update_file
        self.raw_updates = self._load(self.update_file)
        self.people = {}

    @staticmethod
    def _load(infile):
        """
        Load pickled data from the provided file.
        """
        return pickle.load(open(infile, 'rb'))

    def _add_new_person(self, bio, segments):
        person = {
            'bio': bio,
            'segments': segments
        }
        self.people[str(uuid.uuid4())] = person

    def segment(self):
        """
        Process the raw update data into Person objects.
        """
        for page in self.raw_updates.itervalues():
            segments = dict()
            # Exact weekday varies from year to year, so extract when updates
            # were due for the current page.
            breaks = re.findall(r'(?:Jan|Feb|Mar|Apr|May) \d\d?', page)
            if len(breaks) == 0:
                continue # Skip non-update pages

            bio = page[:page.find(breaks[0])]
            for i, brk in enumerate(breaks):
                # Grab and save from the current break to the next break.
                try:
                    segments[brk] = self.seg_helper(page[page.find(breaks[i]):
                                                         page.find(breaks[i+1])])
                except IndexError:
                    # Last segment is from current break to end of string
                    segments[brk] = self.seg_helper(page[page.find(breaks[i]):])

            self._add_new_person(bio, segments)

    def seg_helper(self, seg):
        one = seg.find('What I did:')
        two = seg.find('What I did to develop my professional awareness and/or my human network:')
        three = seg.find('How long I spent:')
        four = seg.find('What I plan to do next week:')
        try:
            split = {
                'did': seg[one + 10:two],
                'pro': seg[two + 71:three],
                'hrs': seg[three:four],
                'fut': seg[four:]
            }

            hrsexpr = r'How long I spent:\n?(.*?)(?:Recall that you .+\))?(.*)'
            matches = re.findall(hrsexpr, split['hrs'])
            if not matches:
                split['hrs'] = -1

            elif matches:
                for match in matches[0]:
                    discard_expr = r'@|http|Don\'t|Update'
                    if not re.findall(discard_expr, match):
                        clean_expr = r'(\d{1,2}(?:\.5)?) ?(?:hrs?|hours?)'
                        stripped = re.findall(clean_expr, match, re.IGNORECASE)
                        if stripped:
                            split['hrs'] = float(stripped[0])
                        else: # Entries without a time unit?
                            try:
                                tim = float(match)
                                if tim < 15:
                                    split['hrs'] = tim
                                else: # Probably minutes: toss out
                                    split['hrs'] = -1
                            except ValueError:
                                split['hrs'] = -1

        except TypeError:
            split = {}
        return split

if __name__ == "__main__":
    import json
    pro = Processor('scraped_updates.p')
    pro.segment()
    with open('people.json', 'w') as outfile:
        json.dump(pro.people, outfile)
