import os, scipy.misc, numpy, time
import subprocess
from HTML import Table, TableRow, TableCell
from eb.env import env


class Report():

    def __init__(self, title):

        self.title = title
        self.items = list()
        self.filename = None


    def append(self, item):

        self.items.append(item)
        return self


    def appendReport(self, report):

        assert isinstance(report, Report)
        self.items = self.items + report.items
        return self


    def generateHTML(self, dirname):

        imageCount = 0
        relativeDirname = os.path.basename(dirname)
        html = list()
        html.append('<!DOCTYPE html>')
        html.append('<html lang="en">')
        html.append('  <head>')
        html.append('    <meta charset="ASCII" />')
        html.append('    <title>' + self.title + '</title>')
        html.append('    <link rel="stylesheet" type="text/css" href="' + os.path.join(relativeDirname, 'stylesheet.css"') + ' media="all" />')
        html.append('    <script type="text/javascript" src="' + os.path.join(relativeDirname, 'javascript.js') + '"> </script>')
        html.append('    <noscript> </noscript>')
        html.append('  </head>')
        html.append('  <body>')
        html.append('  <section class="report" id="report0" style="display:block">')
        html.append('    <header>')
        html.append('      <h1> ' + self.title + ' </h1>')
        html.append('    </header>')
        for item in self.items:
            if isinstance(item, ReportImage):
                html = html + item.generateHTML(dirname, imageCount)
                imageCount += 1
            else:
                html = html + item.generateHTML()
        html.append('  </section>')
        html.append('    <footer id="footer">')
        html.append('      <p> generated by <b>' + os.environ.get('USERNAME') + '</b> on ' + time.ctime() + '</p>')
        html.append('    </footer>')
        html.append('  </body>')
        html.append('</html>')

        return html


    def saveHTML(self, filename=env.tempfile('report', '.html')):

        self.filename = filename
        dirname = os.path.splitext(filename)[0] + '_files'
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        html = self.generateHTML(dirname)
        import codecs
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            for line in html:
                f.write(line + '\n')


        import shutil
        shutil.copy(os.path.join(os.path.dirname(__file__), 'javascript.js'), dirname)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'stylesheet.css'), dirname)

        return self


    def open(self):

        cmd = self.filename
        subprocess.call(cmd, shell=True)
        return self


class ReportHeading():

    def __init__(self, title, sub=0):

        assert isinstance(title, basestring)
        self.title = title
        self.sub = sub


    def generateHTML(self):

        #html.append('    <header>')
        #html.append('      <h1> ' + self.title + ' </h1>')
        #html.append('    </header>')

        if self.sub == -1:
            html = ['    <header><h' + str(self.sub + 2) + '> ' + self.title + ' </h' + str(self.sub + 2) + '></header>']
        else:
            html = ['    <h' + str(self.sub + 2) + '> ' + self.title + ' </h' + str(self.sub + 2) + '>']

        return html


class ReportMonospace():

    def __init__(self, text):

        assert isinstance(text, basestring)
        self.text = text


    def generateHTML(self):

        html = list()
        html.append('    <pre><code>')
        html.append(self.text)
        html.append('    </code></pre>')
        return html


class ReportParagraph():

    def __init__(self, text, font_color='black'):

        assert isinstance(text, basestring)
        self.text = text
        self.font_color = font_color


    def generateHTML(self):
        html = list()
        html.append('    <p><font color="' + self.font_color +'">')
        html.append(self.text)
        html.append('    </font></p>')
        return html


class ReportImage():

    def __init__(self, array, caption=''):

        assert isinstance(array, numpy.ndarray)
        assert isinstance(caption, basestring)
        self.array = array
        self.caption = caption


    def generateHTML(self, dirname, imageCount):

        basename = 'image' + str(imageCount) + '.png'
        relativeDirname = os.path.basename(dirname)
        relativeImageFilename = os.path.join(relativeDirname, basename)
        absoluteImageFilename = os.path.join(dirname, basename)

        scipy.misc.toimage(self.array).save(absoluteImageFilename)

        html = list()
        html.append('    <p>')
        html.append('      <img src="' + relativeImageFilename + '"/>')
        html.append('    <br /><i>' + self.caption + '</i></p>')
        return html


class ReportTable():

    def __init__(self, data, caption='', colHeaders=None, rowHeaders=None, colSpans=None, rowSpans=None):

        table = [TableRow([TableCell(str(v)) for v in row]) for row in data]

        if colHeaders is not None:

            if colSpans is None:
                 colSpans = [[None for v in vr] for vr in colHeaders]
            table = [TableRow([TableCell(cell, header=True,  attribs = {'colspan': cscell})
                                 for cell, cscell in zip(row, colSpan)], header=True) for row, colSpan in zip(colHeaders, colSpans)] + table

        if rowHeaders is not None:

            if rowSpans is None:
                rowSpans = [[None for v in vr] for vr in rowHeaders]

            if colHeaders is not None:
                table[0].cells.insert(0, TableCell('', header=True, attribs={'colspan':len(colHeaders), 'rowspan': len(rowHeaders)}))

            for rowheader, rowspan  in reversed(zip(rowHeaders, rowSpans)):
                i = len(colHeaders) if colHeaders is not None else 0
                for header, span in zip(rowheader, rowspan):

                    table[i].cells.insert(0, TableCell(header, header=True, attribs={'rowspan': span}))
                    i += span if span is not None else 1

        self.table = Table(table)
        self.caption = caption

    def generateHTML(self):

        html = list()
        html.append('    <p>')
        html.append(str(self.table))
        if self.caption != '':
            html.append('    <br /><i>' + self.caption + '</i></p>')
        html.append('    </p>')

        return html


class ReportHorizontalLine():

    def generateHTML(self):

        html = ['    <hr>']
        return html


class ReportHyperlink():

    def __init__(self, url, text):

        self.url = url
        self.text = text

    def generateHTML(self):

        html = ['<p><a href="' + self.url + '" target="_blank">' + self.text +'</a></p>']
        return html


class ReportHTML():

    def __init__(self, html):

        self.html = html

    def generateHTML(self):

        return [self.html]


if __name__ == '__main__':

    import eb

    array = numpy.random.randint(0, 255, [3, 300, 300])
    colHeaders = [['Hello World'], ['A', 'B'], ['a1', 'a2', 'b1', 'b2']]
    colSpans =   [[4],             [2, 2],     [1, 1, 1, 1]]
    rowHeaders = [['Hello World'], ['X', 'Y', 'Z'], ['x1', 'x2', 'y1', 'y2', 'z1', 'z2']]
    rowSpans = [[6], [2, 2, 2], [1, 1, 1, 1, 1, 1]]
    data = numpy.random.randint(0, 5, (6, 4))

    report = Report('Title') \
        .append(ReportHeading('Heading')) \
        .append(ReportHorizontalLine())\
        .append(ReportHeading('SubHeading', 1))\
        .append(ReportHeading('SubSubHeading', 2))\
        .append(ReportHeading('SubSubSubHeading', 3))\
        .append(ReportHeading('SubSubSubSubHeading', 4))\
        .append(ReportMonospace('Monospace text: a = 1 + 3'))\
        .append(ReportParagraph('Paragraph text: The joy of coding Python should be in seeing short, concise, readable classes that express a lot of action in a small amount of clear code -- not in reams of trivial code that bores the reader to death. - Guido van Rossum'))\
        .append(ReportImage(array, 'This is a nice image')) \
        .append(ReportTable(data, 'Table without headers.'))    \
        .append(ReportTable(data, 'Table with column headers.', colHeaders=colHeaders, colSpans=colSpans)) \
        .append(ReportTable(data, 'Table with row headers.', rowHeaders=[rowHeaders[-1]])) \
        .append(ReportTable(data, 'Table with nested column and row headers', colHeaders, rowHeaders, colSpans, rowSpans)) \
        .append(ReportHyperlink('http://www.enmap.org/', 'Visit EnMAP!'))\
        .saveHTML().open()
    print report.filename