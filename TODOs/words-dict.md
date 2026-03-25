Are you relying on `/usr/share/dict/words`
if yes, pls make our implementation OS-dependent.

For examples, copy `/usr/share/dict/words` to our repo <root>/data/words.txt, and read from there instead of `/usr/share/dict/words`.

This way, we can ensure that our implementation works across different operating systems and environments without relying on the presence of a specific file.