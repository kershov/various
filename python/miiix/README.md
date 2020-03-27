```
    _____  ._______  ___ __________
   /     \ |   \   \/  / \______   \_____ _______  ______ ___________
  /  \ /  \|   |\     /   |     ___/\__  \\_  __ \/  ___// __ \_  __ \
 /    Y    \   |/     \   |    |     / __ \|  | \/\___ \\  ___/|  | \/
 \____|__  /___/___/\  \  |____|    (____  /__|  /____  >\___  >__|
         \/          \_/                 \/           \/     \/
```

# MIX Parser

The script connects to the MIIIX.org website and:

1. Authenticates with given credentials.
2. Initiates generation of a file from one of the the two given categories.
   The categories are: Tyres, Rims.
3. Waits until generation is finished.
4. Downloads generated file and saves it at the given path.
5. Optionally uploads downloaded files to a client's FTP-server.
6. Logs all its actions to the system's stdin and log-file.


# MIT License

Copyright (c) 2018 Konstantin Ershov (konstantin.ershov@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
