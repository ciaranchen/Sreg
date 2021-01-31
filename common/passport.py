from enum import Enum

class PassportType(Enum):
    USER = 1
    PHONE = 2
    EMAIL = 3


    @staticmethod
    def get_string(x):
        return ['user', 'phone', 'email'][x.value - 1]


    @staticmethod
    def get_passport_type(x: str):
        return {'user': PassportType.USER, 'phone': PassportType.PHONE, 'email': PassportType.EMAIL}[x]


class PassportEncoder(list):
    def add_passport(self, _type, passports):
        if passports:
            for passport in passports.split(','):
                self.append((_type, passport.strip()))


    def get_types(self):
        return set([t for t, p in self])


    def get_output(self):
        passport_types = [PassportType.USER, PassportType.PHONE, PassportType.EMAIL]
        passports = {ti: [p for t, p in self if t == ti] for ti in passport_types}
        msg = ['[+] ' + PassportType.get_string(ti).capitalize() + ' Checking: ' + ', '.join(passports[ti]) for ti in passport_types if len(passports[ti]) > 0]
        return '\n' + '\n'.join(msg)
