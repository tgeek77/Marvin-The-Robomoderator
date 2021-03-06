#!/usr/local/bin/python
#
#    MarvinTheRoboModerator v0.01a
#    Copyright (C) 2001  Kai Puolam?ki <Kai.Puolamaki@iki.fi>
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

import nntplib, string, robo

(name, port) = robo.getnntpserver()

server = nntplib.NNTP(name, port)
response, list = server.list()
server.quit()

response = string.atoi(string.split(response)[0])
if response >= 200 and response < 300:
    for tuple in list:
        if tuple[3] == "y":
            print tuple[0]
