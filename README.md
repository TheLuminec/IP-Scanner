This is a IP-Scanner i'm testing.

use-
nmap3
sqlite3

somthing that multthreads

Will be pinging many ips at once to minimize downtime,

Steps per thread:
Get next iterated IP
Ping - if no response log dead
Port scan - 0-65535
if web flag was set than log to web-port
if has any non closed port log to ported
log to alive
give thread new iterated IP

-Sorting will come later after mass data collection

Will use seperate databases
1. dead - doesn't respond
2. alive - responds
3. ported - has at least one port not closed
4. good-port - has 433 / 80 / 22 open
