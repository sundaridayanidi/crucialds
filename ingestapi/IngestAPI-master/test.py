from encrypt import AESCipher

if __name__ == "__main__":
    s = "my name is scotland"
    key = "zircon"
    crypto = AESCipher(key)
    cipher = crypto.encrypt(s)
    plaintext = crypto.decrypt(cipher)

    print "the cipher text is " + str(cipher)
    print "the plaintext is " + str(plaintext)

