#!/usr/local/bin/python
#
#    MarvinTheRoboModerator v0.01a
#    Copyright (C) 2001  Kai Puolam‰ki <Kai.Puolamaki@iki.fi>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


import rfc822, string, StringIO, nntplib, smtplib, os

def postarticle(article):
    (name, port) = getnntpserver()
    fp = StringIO.StringIO(article)
    s = nntplib.NNTP(name, port)
    s.post(fp)
    s.quit()
    fp.close()

def removecontrols(msg):
    i = 0
    table = ""
    while i < 256:
        if i < 32 and not (chr(i) == "\n" or chr(i) == "\t" or chr(i) == "\f"):
            table = table + "_"
        else:
            table = table + chr(i)
        i = i + 1
    return string.translate(msg, table, "\r")


def striplist(list):
    result = []
    for s in list:
        s = string.strip(s)
        if s:
            result.append(s)
    return result

def getenviron(name, default = None):
    if name in os.environ.keys():
        return os.environ[name]
    else:
        return default

def getnntpserver():
    name = getenviron("NNTPSERVER", "news.cc.tut.fi")

    colon = string.find(name, ":")
    if colon == -1:
        port = 119
    else:
        name, port = name[:colon], string.atoi(name[colon+1:])

    return (name, port)


class Article(rfc822.Message):
    def __init__(self, fp, seekable = 1):
        rfc822.Message.__init__(self, fp, seekable)
        self.body = self.fp.readlines()
        self.strippedbody = striplist(self.body)
        self.myname = getenviron("ROBOMYNAME", "sfnet.test")
        self.approveemail = getenviron("ROBOAPPROVEEMAIL", \
                                       "sfnet-test-request@foo.example")
        self.noreplyemail = getenviron("ROBONOREPLYEMAIL", \
                                       "noreply@foo.example")
        self.head = self.allheaders()
        
    def newsgroups(self, name):
        content = self.getheader(name)
        if content:
            return striplist(string.split(self.getheader(name), ","))
        else:
            return None

    def allheaders(self):
        headers = []
        new = ""
        for line in self.headers:
            if new:
                if line[0] == " " or line[0] == "\t":
                    new = new + line
                else:
                    headers.append(new)
                    new = line
            else:
                new = line
        headers.append(new)
        return headers

    def removeheader(self, name):
        self.removeheaders([name])

    def removeheaders(self, names):
        headers = []
        removes = []
        for name in names:
            removes.append(string.lower(name) + ":")
        for line in self.head:
            colon = string.find(line, ":") + 1
            if colon > 0:
                if not string.lower(line[:colon]) in removes:
                    headers.append(line)
        self.head = headers

    def addheader(self, name, content):
        self.head.append(name + ": " + content + "\n")

    def getheader(self, name, default=None):
        name = string.lower(name) + ":"
        length = len(name)
        for line in self.head:
            if name == string.lower(line[:length]):
                return string.strip(line[length:])
        return default

    def getheaders(self, name, default = None):
        name = string.lower(name) + ":"
        length = len(name)
        result = []
        for line in self.head:
            if name == string.lower(line[:length]):
                result.append(string.strip(line[length:]))
        if len(result) == 0:
            return default
        return result

    def fixnewsgroups(self, name):
        groups = self.newsgroups(name)
        self.removeheader(name)
        self.addheader(name, string.join(groups, ","))

    def removeduplicates(self, name):
        content = self.getheader(name)
        self.removeheader(name)
        self.addheader(name, content)
    
    def lint(self):
        self.linthead()
        self.lintbody()

    def linthead(self):
        new = []
        for line in self.head:
            new.append(removecontrols(line))
        self.head = new
        if self.getheader("newsgroups"):
            groups = self.newsgroups("newsgroups")
            if not self.myname in groups:
                groups.append(self.myname)
                self.removeheader("newsgroups")
                self.addheader("Newsgroups", string.join(groups, ","))
            self.fixnewsgroups("Newsgroups")
        else:
            self.addheader("Newsgroups", self.myname)
        if self.getheader("followup-to"):
            self.fixnewsgroups("Newsgroups")
        self.removeheaders(["distribution", "path", "nntp-posting-host", \
                            "status", "lines", "received", "apparently-to", \
                            "cc", "message-id", "sender", "in-reply-to", \
                            "x-vm-v5-data", "originator", "return-path"])
        subject = self.getheader("subject")
        if subject and (subject[:3] == "Vs:" or subject[:3] == "Sv:"):
            self.removeheader("subject")
            self.addheader("Subject", "Re:" + subject[3:])
        if not self.getheader("organization"):
            self.addheader("Organization", "-")
        self.addheader("Path", "robomoderator!not-for-mail")

    def lintbody(self):
        new = []
        for line in self.body:
            new.append(removecontrols(line))
        self.body = new

    def runtests(self, tests):
        message = ""
        for test in tests:
            t = test(self)
            m = t.message
            if m:
                message = message + m + "\n\n"
        if not message:
            return None
        return message

    def approve(self):
        article = string.join(self.head, "")
        article = article + "Approved: " + self.approveemail + "\n"
        article = article + "X-Comment: Moderators do not necessarily agree or disagree with this article.\n"
        article = article + "X-Policy: http://www.cs.tut.fi/sfnet/sfnet.test.html\n"
        article = article + "X-Comment-2: I am really just testing the robomoderator...\n"
        article = article + "\n" + string.join(self.body, "")
        return article

    def getreplyheader(self):
        message = ""
        precedence = self.getheader("precedence")
        if precedence:
            precedence = string.lower(precedence)
            if precedence == "junk" or precedence == "bulk" or \
               precedence == "list":
                return None
        loops = self.getheaders("x-loop")
        if loops:
            for loop in loops:
                if string.lower(loop) == string.lower(self.noreplyemail):
                    return None
                message = message + "X-Loop: " + loop + "\n"
        noconfirm = self.getheader("x-no-confirm")
        if noconfirm and string.lower(noconfirm) == "yes":
            return None
        subject = self.getheader("subject")
        if not subject:
            subject = "(no subject)"
        if string.find(subject, "[auto-reply]") >= 0:
            return None
        (name, email) = self.getaddr("reply-to")
        if not email:
            (name, email) = self.getaddr("from")
            if not email:
                return None
        if name:
            message = message + "To: " + name + " <" + email + ">\n"
        else:
            message = message + "To: " + email + "\n"
        self.senderemail = email
        message = message + "Subject: [auto-reply] " + subject[:60] + "\n"
        mid = self.getheader("message-id")
        if mid:
            message = message + "References: " + mid + "\n"
            message = message + "In-Reply-To: " + mid + "\n"
        message = message + "Precedence: junk\n"
        message = message + "X-Loop: " + self.noreplyemail + "\n"
        message = message + "Mime-Version: 1.0\n"
        message = message + "Content-Type: text/plain; charset=iso-8859-1\n"
        message = message + "Content-Transfer-Encoding: 8bit\n"
        message = message + "From: " + self.myname + \
                  " robomoderaattori <" + self.noreplyemail + ">\n"
        return message
        
    def sendemail(self, msg):
        name = getenviron("SMTPSERVER", "varis.cs.tut.fi")
        s = smtplib.SMTP(name)
        s.sendmail(self.noreplyemail, self.senderemail, msg)
        s.quit()
    
        
        
        

class ArticleTest:
    __message__ = """Prototype message."""

    def __init__(self, article):
        self.article = article
        self.myname = self.article.myname
        self.message = self.test()

    def test(self):
        pass
            

class isBinary(ArticleTest):
    def test(self):
        maxbinlines = 0
        nbinlines = 0
        for line in self.article.body:
            line = string.strip(line)
            if(len(line) > 45 and string.find(line, " ") == -1 and \
               string.find(line, "\t") == -1):
                nbinlines = nbinlines + 1
                if nbinlines > 10:
                    return self.__message__
            else:
                nbinlines = 0

        s = self.article.getheader("content-type")
        if s and string.find(string.lower(s), "text/plain") == -1:
            return self.__message__

        return None

    __message__ = """Artikkeli sis‰lt‰‰ bin‰‰ridataa, HTML:‰‰ tai liitetiedostoja."""
            
                
class badSignature(ArticleTest):
    def test(self):
        nsignature = -1
        for line in self.article.body:
            if nsignature >= 0:
                nsignature = nsignature + 1
            else:
                if line == "--\n":
                    return self.__message__
                if line == "-- \n":
                    nsignature = 0
        if nsignature > 6:
            return self.__message__
        return None
        
    __message__ =  """Signature alkaa separaattoririvin j‰lkeen.  Separaattoririvin koostuu
kahdesta viivasta, v‰lilyˆnnist‰ ja rivinvaihdosta ("-- ").  Signaturen
pituuden tulisi olla korkeintaan 4 rivi‰."""

class overQuote(ArticleTest):
    def test(self):
        prefixes = {}
        for line in self.article.strippedbody:
            if line and not line[0] in string.letters:
                if prefixes.has_key(line[0]):
                    prefixes[line[0]] = prefixes[line[0]] + 1
                else:
                    prefixes[line[0]] = 1

        maxquot = max(20, 0.5*len(self.article.strippedbody))

        for prefix in prefixes.keys():
            if prefixes[prefix] > maxquot:
                return self.__message__

        return None

    __message__ = """Artikkelissa on liikaa lainattua teksti‰.  Lainattua teksti‰ tulisi
karsia ja omat kommentit tulisi kirjoittaa lainauksen j‰lkeen."""

class megaCrosspost(ArticleTest):
    def test(self):
        
        followups = self.article.newsgroups("followup-to")
        groups = self.article.newsgroups("newsgroups")
        if len(groups) > 4:
            return self.__message__

        if followups:
            if len(followups)>1 and self.myname in followups:
                return self.__message__
        else:
            if len(groups) > 1:
                return self.__message__

        return None

    __message__ = """Artikkeli on crosspostattu liian moneen uutisryhm‰‰n."""


class validGroups(ArticleTest):
    def test(self):
        groups = self.article.newsgroups("newsgroups")
        if len(groups) == 1 and groups[0] == self.myname:
            return None
        f = open("validgroups")
        validgroups = striplist(f.readlines())
        f.close()
        for group in groups:
            if not (group == self.myname or group in validgroups):
                return self.__message__

        return None

    __message__ = """Artikkeli on crosspostattu toiseen moderoituun uutisryhm‰‰n tai
tuntemattomaan uutisryhm‰‰n."""

class subjectVs(ArticleTest):
    def test(self):
        s = self.article.getheader("subject")
        if s[:3] == "Vs:" or s[:3] == "Sv:":
            return self.__message__
        return None

    __message__ = """Artikkelin otsikko alkaa merkkijonoilla "Vs:" tai "Sv:", kun oikea
merkkinojo olisi "Re:"."""

class isControl(ArticleTest):
    def test(self):
        if self.article.getheader("control") or \
           self.article.getheader("supersedes"):
            return self.__message__
        s = self.article.getheader("subject")
        if s and string.strip(string.lower(s[:5])) == "cmsg":
            return self.__message__
        return None

    __message__ = """Artikkeli on kontrolliviesti (esimerkiksi cancel-viesti)."""

