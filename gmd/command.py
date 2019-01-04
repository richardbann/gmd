import logging


class ParseException(Exception):
    pass


class Command:
    def __init__(self, options=None, mutexopts=None):
        self.options = options
        self.mutexopts = mutexopts

    def next_options(self, parsed_options):
        # based on the parsed options we can work out forbidden options
        # given by mutexopts
        forbidden = set()
        for o in parsed_options:
            for mutex in self.mutexopts or []:
                for mg in mutex:
                    if o not in mg:
                        continue
                    m = 'parsed option {} is in mutex group {}'.format(o, mg)
                    logging.debug(m)
                    for omg in mutex:
                        if omg == mg:
                            continue
                        forbidden |= set(omg)

        logging.debug('parsed options:')
        for w in parsed_options:
            logging.debug(w)
        logging.debug('forbidden:')
        for w in forbidden:
            logging.debug(w)

        ret = []
        for o in self.options:
            if o.name in parsed_options:
                if o.many is True:
                    ret.append(o)
                continue
            if o.name in forbidden:
                continue

            ret.append(o)
        return ret

    def parse_options(self, words):
        """
        Returns:
            - a mapping of option_name, values
            - the unparsed words
            - an option instance we are completing (option arg) OR None
        """
        m = {}
        u = words.copy()

        while u:
            next = self.next_options(m)
            if not u[0].startswith('-'):
                return m, u, None
            opt = [
                o for o in next
                if u[0] == '-' + o.short_name or u[0] == '--' + o.name
            ]
            if not opt:
                raise ParseException('Invalid option: {}'.format(u[0]))
            opt = opt[0]
            u.pop(0)

            # option arg?
            if opt.typ != 'B':
                if not u:
                    return m, u, opt
                arg = u.pop(0)
                if opt.name in m:
                    m[opt.name].append(arg)
                elif opt.many is True:
                    m[opt.name] = [arg]
                else:
                    m[opt.name] = arg
            else:
                m[opt.name] = True

        return m, u, None

    def complete(self, sofar):
        # map, unparsed, completing
        try:
            m, u, c = self.parse_options(sofar)
        except ParseException as e:
            return "_message '{}'".format(e)

        if c is None:
            logging.debug('----------')
            n = self.next_options(m)
            s = ['-{}:"{}"'.format(opt.short_name, opt.help) for opt in n]
            s += ['--{}:"{}"'.format(opt.name, opt.help) for opt in n]
            # Use tag "opts" not "options"; those would not show up by default
            return "_alternative 'opts:options:(({}))'".format(' '.join(s))
        else:
            return "_alternative 'files:config files:_files'"


class Option:
    def __init__(
        self, name, short_name=None, help='', typ='S', many=False
    ):
        self.name = name
        self.short_name = short_name
        self.help = help
        self.typ = typ
        self.many = many
