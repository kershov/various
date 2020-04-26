__version__ = '1.0'


class ConfigLineParser:
    def __init__(self, line=None):
        self._config = {}

        if line:
            self.parse_line(line)

    def parse_line(self, line):
        if line.startswith('#'):
            return

        if '#' in line:
            line = line.split('#', 1).pop(0)

        if '=' not in line:
            return

        key, value = line.split('=', 1)
        key, value = key.strip().lower(), value.strip()

        self._config[key] = value

        return self.get_config()

    def get_config(self):
        return self._config

    def get_value(self, key):
        return self._config.get(key, None)


class ConfigFileParser(ConfigLineParser):
    def __init__(self, file, *args, **kwargs):
        super(ConfigFileParser, self).__init__(*args, **kwargs)

        self._file = file
        self._parse(self._file)

    def _parse(self, file):
        with open(file) as f:
            for line in f.readlines():
                self.parse_line(line)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del self

    def __repr__(self):
        return f'{self.__class__.__name__}({str(self.get_config())})'


def main():
    import sys
    file = 'config.conf' if len(sys.argv) == 1 else sys.argv[1]

    line_config_parser = ConfigLineParser('# Hello World')
    assert not line_config_parser.get_config()

    line_config_parser = ConfigLineParser('VAR1 = 12345 # Comment')
    assert line_config_parser.get_value('var1') == '12345'

    line_config_parser.parse_line('VAR2')
    assert not line_config_parser.get_value('var2')

    try:
        with ConfigFileParser(file) as config:
            print(config)
            print(config.get_config())
            print(f"The city is: {config.get_value('city')}")
            print(f"Non-existent key 'THE_KEY': {config.get_value('the_key')}")
    except IOError as e:
        import sys
        print(f"Cannot open file '{file}': {e}.", file=sys.stderr)


if __name__ == '__main__':
    main()
