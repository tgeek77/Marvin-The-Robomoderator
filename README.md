## Marvin The Robomoderator

Found at http://users.ics.aalto.fi/kaip/marvin/

Created by Kai Puolamäki

### Original description:

Marvin is a robomoderator. Marvin will moderate a newsgroup,
automagically and without human intervention, except when something goes
wrong. Everything is untested and under developement. You have been
warned.

Essentially Marvin does the following:

1.  It receives mail sent to submission address
2.  It fixes some typical mistakes in the headers ("lint")
3.  It makes some checks to determine if the article will be rejected
4.  It makes some checks to determine whether the author should be
    warned (e.g. too long signature)
5.  If there were no grounds for rejection it will post the article.
6.  If it seems to be ok to send autoreply (no mail loops and the author
    has not requested no autoreplies) Marvin will compose and send an
    autoreply. If there were warnings (e.g. too long signatures) the
    Marvin will mention them in the autoreply. If the article was
    rejected, Marvin will list the reasons.

Marvin is written mostly in Python, with some small parts implemented in
Bourne Shell script. Tests for the article are implemented as Python
classes, which makes it easy to customize the rejection or warning
criteria or to add more of the same stuff later on. The news article
class (which takes care of most of the technical fluff) is implemented
as a subclass of the standard rfc822.Message object.

See the COPYING file for the text of the GPL 2.0 license.