# Class that defines the Password object. Object will match values of the table: tblPassword

import hashlib
import string
import random

from fitflex.DBConnect import DBAction,DBQuery

class Password:
    
    def hash_password(self, password, salt):
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    # Returns True or False.
    def login(self, email, password):

        # Get password hash and salt.
        hashSalt = DBQuery("exec spGetPasswordHash @email ='"+email+"'")
        try:
            if(len(hashSalt[0])>3):
                output = (hashSalt[0])[2:len(hashSalt[0])-2]
                output = output.split("', '")
                temphash = output[0]
                tempsalt = output[1]

                # Generate password.
                generatedPassword = self.hash_password(password, tempsalt)

                #Compare passwords.
                if temphash == generatedPassword:
                    return True
                return False
            print("error")
        except:
            return False

    # Create password. This is only called during user creation.
    def create(self, password):

        # Create Salt.
        salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=25))
        # Create Hash.
        passhash = self.hash_password(password, salt)
        DBAction("EXEC spPasswordInsert @Salt='"+ salt +"', @Hash='"+ passhash + "'")

        tempstr = DBQuery("select passID from tblPassword where passSalt = '"+ salt +"' and passHash='"+ passhash +"'")[0]
        passid = int(tempstr[1:len(tempstr)-2])
        return passid

    # Update Password. Password reset.
    def update(self, userEmail, currentPassword, newPassword):
        # Fetch current password hash and salt from the database.
        hashSalt = DBQuery("exec spGetPasswordHash @Email = '"+ userEmail +"'")
        if(len(hashSalt[0])>3):
            output = (hashSalt[0])[2:len(hashSalt[0])-2]
            output = output.split("', '")
            tempHash = output[0]
            tempSalt = output[1]

            # Check if the current password matches the provided currentPassword.
            # Negating to do a test password update.
            if self.hash_password(currentPassword, tempSalt) == tempHash:
                # Generate new salt and hash for the newPassword.
                newSalt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=25))
                newHash = self.hash_password(newPassword, newSalt)

                # Update the password in the database with the new salt and hash.
                DBAction("EXEC spPasswordUpdate @Email='" + userEmail + "', @Salt='" + newSalt + "', @Hash='" + newHash + "'")
                return True
            else:
                # Current password does not match.
                return False
        else:
            # Error fetching current password hash and salt.
            return False

