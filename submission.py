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

generaldescr = \
"""Uutisryhm‰n sfnet.test kuvaus on:
 
  sfnet.test Nyyssij‰rjestelm‰n toiminnan testaamiseen
 
  Yleinen testausryhm‰, johon l‰hetettyyn viestiin yleens‰ tulee
  joukko automaattivastauksia eri palvelimilta. Aloittelijoille ja
  yleens‰ kokeiluihin sopii paremmin ryhm‰ sfnet.aloittelijat.testit.
 
Uutisryhm‰n WWW-sivu: http://www.cs.tut.fi/sfnet/sfnet.test.html
 
Vaihtoehtoinen moderoimaton uutisryhm‰: news:sfnet.aloittelijat.testit

Uutisryhm‰n kuvauksesta ja moderointipolitiikasta voi keskustella ryhm‰ss‰:
news:sfnet.ryhmat+listat
 
Moderointia koskevat _tekniset_ kommentit voi l‰hett‰‰ osoitteeseen:
kaip+sfnet-test-request@cs.tut.fi (ƒl‰ odota nopeaa vastausta...)

""" 

import robo, sys, string, os

warn = [robo.badSignature, robo.subjectVs]

reject = [robo.isBinary, robo.overQuote, robo.megaCrosspost, \
          robo.validGroups, robo.isControl]

a = robo.Article(sys.stdin)

replyheader = a.getreplyheader()
replybody = \
"""[This is an automated reply to an article posted to a Finnish-language
moderated newsgroup sfnet.test.  See http://www.example/english.html
for further information.]
 
[T‰m‰ on automaattisesti l‰hetetty vastaus uutisryhm‰‰n sfnet.test
l‰hett‰m‰‰si artikkeliin.  Jos et halua saada automaattivastauksia, niin
lis‰‰ artikkeliisi seuraava otsikkokentt‰: "X-No-Confirm: yes"]

"""

originalheader = string.join(a.headers, "")
originalbody = string.join(a.body, "")
originalarticle = originalheader + "\n" + originalbody

f = open(os.tempnam(os.getcwd() + "/archive", "rec."), "w")
f.write(originalarticle + "\n***\n")

a.lint()
warnings = a.runtests(warn)
rejects = a.runtests(reject)
if rejects:
    replybody = replybody + \
"""Olen pahoillani, mutta robomoderaattori on hyl‰nnyt uutisryhm‰‰n
sfnet.test l‰hett‰m‰si artikkelin.  Artikkelia ei postiteta kyseiseen
uutisryhm‰‰n. """ + generaldescr + \
"""Artikkelisi hyl‰ttiin seuraavista syist‰:

""" + rejects + \
"""Terveisin, Marvin (robomoderaattori)
"""
else:
    replybody = replybody + \
"""Artikkelisi on hyv‰ksytty uutisryhm‰‰n sfnet.test.  Artikkelisi
pit‰isi n‰ky‰ paikallisella uutispalvelimellasi vuorokauden kuluessa.
(Yleens‰ artikkelit levi‰v‰t minuuteissa, mutta joskus
nyyssij‰rjestelm‰ on v‰h‰n ep‰luotettava...)
 
""" + generaldescr + \
"""
Terveisin, Marvin (robomoderaattori)
"""
    postedarticle = a.approve()
    robo.postarticle(postedarticle)
    f.write(postedarticle + "\n***\n")
    

if warnings:
    replybody = replybody + \
"""
PS. Automaattinen tarkistin lˆysi artikkelistasi joitain ep‰ilytt‰vi‰
rakenteita.  Artikkelit hyv‰ksyt‰‰n n‰ist‰ rakenteista huolimatta.
Yrit‰ kuitenkin korjata asia seuraavissa postauksissasi.
 
Tarkistimen lˆyt‰m‰t ep‰ilytt‰v‰t rakenteet:

""" + warnings

replybody = replybody + \
"""

Alkuper‰inen artikkelisi (ensimm‰iset kaksi kilotavua):

"""

replybody = replybody + originalarticle[:2048]

if replyheader:
    f.write(replybody + "\n***\n")
    try:
        a.sendemail(replyheader + "\n" + replybody)
    except:
        f.write("\n*** Sending mail failed.\n")


f.write("\n***end***\n")
f.close()

