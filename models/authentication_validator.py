"""
Script description: This script provides string validations for various user inputs. 

Libraries imported:
- re: Module implementing regular expressions.
"""

import re


class Validator:
    """
    This class will check the validity of the entered username, name, and email for a 
    newly registered user.
    """

    def __init__(self, mail_whitelist: list[str]):
        self.mail_whitelist = mail_whitelist

    def validate_email(self, email: str) -> bool:
        """
        Checks the validity of the entered email.

        Parameters
        ----------
        email: str
            The email to be validated.
            
        Returns
        -------
        bool
            Validity of entered email.
        """
        pattern = r"^[a-zA-Z0-9._%+-]{1,254}@[a-zA-Z0-9.-]{1,253}\.[a-zA-Z]{2,63}$"
        if bool(re.match(pattern, email)):
            domain = email.split("@")[1]
            return domain in self.mail_whitelist
        return False

    def validate_length(self, variable: str, min_length: int = 0, max_length: int = 254) -> bool:
        """
        Checks the length of a variable.
        
        Parameters
        ----------
        variable: str
            The variable to be validated.
        min_length: str
            The minimum required length for the variable.
        max_length: str
            The maximum required length for the variable.

        Returns
        -------
        bool
            Validity of entered variable.
        """
        pattern = rf"^.{{{min_length},{max_length}}}$"
        return bool(re.match(pattern, variable))

    def validate_name(self, name: str) -> bool:
        """
        Checks the validity of the entered name.
        
        Parameters
        ----------
        name: str
            The name to be validated.
            
        Returns
        -------
        bool
            Validity of entered name.
        """
        pattern = r"^[A-Za-z. ]{2,100}$"
        return bool(re.match(pattern, name))

    def validate_password(self, password: str) -> bool:
        """
        Checks the validity of the entered password.
    
        Parameters
        ----------
        password: str
            The password to be validated.
            
        Returns
        -------
        bool
            Validity of entered password.
        """

        special_chars = r"!@#$%^&*(),.?\":{}|<>_\-\[\]~`+=/\\"

        if not 8 <= len(password) <= 20:
            return False

        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))

        has_special = any(char in special_chars for char in password)

        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' + special_chars)
        has_valid_chars = all(char in valid_chars for char in password)

        return all([has_upper, has_lower, has_digit, has_special, has_valid_chars])

    def validate_username(self, username: str) -> bool:
        """
        Checks the validity of the entered username.

        Parameters
        ----------
        username: str
            The username to be validated.
            
        Returns
        -------
        bool
            Validity of entered username.
        """
        pattern = r"^([a-zA-Z0-9_-]{1,20}|[a-zA-Z0-9._%+-]{1,254}@[a-zA-Z0-9.-]{1,253}\.[a-zA-Z]{2,63})$"
        return bool(re.match(pattern, username))
