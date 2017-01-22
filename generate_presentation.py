#! -*- coding: utf-8 -*-

"""
lottery_presentation/generate_presentation.py

Generates a ppt presentation from csv dump of admission lottery results.

column headers (in order):
    id
    lottery_number
    first_name
    last_name
    Elementary

...
"""

import argparse
import csv
from queue import Queue

from pptx import Presentation


def parse_args():
    """
    Setup the input and output arguments for the script.
    Return the parsed input and output files.
    """
    parser = argparse.ArgumentParser(description=\
        "Create a PowerPoint presentation from a csv of lottery results"
    )
    parser.add_argument('infile',
                        type=argparse.FileType('r'),
                        help='CSV file to read in'
    )
    parser.add_argument('outfile',
                        type=argparse.FileType('w'),
                        help='Output powerpoint'
    )
    return parser.parse_args()

class PresentationMaker():
    """
    """

    TEMPLATE_FILENAME = "template.pptx"
    TITLE_SLIDE_LAYOUT_INDEX = 0
    BODY_SLIDE_LAYOUT_INDEX = 1
    BODY_TEXT_PLACEHOLDER_INDEX = 1
    MAX_EXTRA_BULLETS = 5 # in addition to first bullet on a body slide
    ROW_TEMPLATE = "{first_name} {last_name} - {Elementary}"
    #WAITLIST_ROW_TEMPLATE = "" ?

    def __init__(self, infile_name, outfile_name):
        self.infile_name  = infile_name
        self.outfile_name = outfile_name
        self.presentation = Presentation(self.TEMPLATE_FILENAME)
        self.title_layout = self.presentation.slide_layouts[self.TITLE_SLIDE_LAYOUT_INDEX]
        self.body_layout  = self.presentation.slide_layouts[self.BODY_SLIDE_LAYOUT_INDEX]
        self.body_queue   = Queue()

    def make_presentation(self):
        """
        Saves a pptx as self.outfile_name.
        """

        self._add_title_slide("Admitted Students")

        with open(self.infile_name) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                # process enrolled slides
                if row['lottery_number'] == "Offered":
                    self._add_to_body(row)
                else:
                    # at some point switches to waitlist students
                    self._end_body_section()
                    self._add_title_slide("Waitlist Students")
                    self._add_to_body(row)
                    break
            # process the waitlist students
            for row in reader:
                self._add_to_body(row)
                #break

        self._end_body_section()
        self.presentation.save(self.outfile_name)


    def _add_title_slide(self, title_string=''):
        """
        """
        
        slide = self.presentation.slides.add_slide(self.title_layout)
        slide.shapes.title.text = title_string


    def _add_body_slide(self):
        """
        """

        body_slide = self.presentation.slides.add_slide(self.body_layout)
        #body_slide.shapes.title.text = "Body slide title text"
        body_shape = body_slide.shapes.placeholders[self.BODY_TEXT_PLACEHOLDER_INDEX]
        text_frame = body_shape.text_frame

        text_frame.text = self.ROW_TEMPLATE.format(**self.body_queue.get())

        while self.body_queue.qsize():
            new_bullet = text_frame.add_paragraph()
            new_bullet.text = self.ROW_TEMPLATE.format(**self.body_queue.get())

    def _add_to_body(self, row_dict):
        """
        """

        self.body_queue.put(row_dict)
        if self.body_queue.qsize() > self.MAX_EXTRA_BULLETS:
            self._add_body_slide()


    def _end_body_section(self):
        """
        """
        if self.body_queue.qsize():
            self._add_body_slide()


if __name__ == "__main__":

    args = parse_args()
    presentation = PresentationMaker(args.infile.name, args.outfile.name)
    presentation.make_presentation()



    # add title slide with text "Admitted students"

    # add student info body slides until WL

    # add title slide with text "Waitlist"

    # add WL students body slides