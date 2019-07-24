import base64
import rsa

DefaultRSAPublicKeyModulus = "AE47B04D3A55A5FDABC612A426D84484BCB1C29C63BBAC33544A1BB94D930772E6E201CF2B39B5B6EDED1CCCBB5E4DCE713B87C6DD88C3DBBEE3A1FBE220723F01E2AA81ED9497C8FFB05FF54A3E982A76D682B0AABC60DBF9D1A8243FE2922E43DD5DF9C259442147BBF4717E5ED8D4C1BD5344DD1A8F35B631D80AB45A9BC7"

# DefaultRSAPublicKeyExponent 默认的公钥指数
DefaultRSAPublicKeyExponent = 0x10001

# DefaultRSAPrivateKey 默认的私钥
DefaultRSAPrivateKey = '''-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCuR7BNOlWl/avGEqQm2ESEvLHCnGO7rDNUShu5TZMHcubiAc8r
ObW27e0czLteTc5xO4fG3YjD277jofviIHI/AeKqge2Ul8j/sF/1Sj6YKnbWgrCq
vGDb+dGoJD/iki5D3V35wllEIUe79HF+XtjUwb1TRN0ajzW2MdgKtFqbxwIDAQAB
AoGAW0CoHFe9/tLq/SRHlRtKDSJsBRUz11Fb8vd2urjWkmDkaVQ/MEfgUK8Vpy2/
saoVvQ5JkqPud3b45WGsbINGrb8saugZ1h5huDbuxVXKDj1ZWyJPkmxHLUK2+7iL
5c7F7+v2C+n6polIgMV9SbLXD6YIXUJ+GengWQffhTRE7WECQQDj/g5x7Rj5vc7X
o3i0SQmyN4RcxxOWfiLe5OUASKM2UPVBQKI3CugkmiTaXTi7auuG3I4GVPRHVHw9
y/Ekz7J3AkEAw7B5+uI60MwcDMeGoXAMAEYe/s7LhyBICarY6cNwySb46B7OHEUz
ooFV2qx31I6ivpMRwCqrRKXEvjPEAfPlMQJAGrXi/1nluSyRlRXjyEteRXDXov73
voPclfx/D79yz6RAd3qZBpXSiKc+dg7B3MM0AMLKKNe/HrQ5Mgw4njVvFQJAPKvX
ddh0Qc42mCO4cw8JOYCEFZ5J7fAtRYoJzJhCvKrvmxAJ+SvfcW/GDZFRab57aLiy
VTElfpgiopHsIGrc0QJBAMliJywM9BNYn9Q4aqKN/dR22W/gctfa6bxU1m9SfJ5t
5G8MR8HsB/9Cafv8f+KnFzp2SncEu0zuFc/S8n5X5v0=
-----END RSA PRIVATE KEY-----'''

class Encrypt(object):
    def __init__(self, publicKey):
        self.publicKey = publicKey
 
    def encrypt_nopadding(self, message):
        n = int(self.publicKey, 16)
        rsa_pubkey = rsa.PublicKey(n, DefaultRSAPublicKeyExponent)
        crypto = self._encrypt(message.encode(), rsa_pubkey)
        return crypto.hex()
 
    def _pad_for_encryption(self, message, target_length):
        message = message[::-1]
        max_msglength = target_length - 11
        msglength = len(message)
        padding = b''
        padding_length = target_length - msglength - 3
        for i in range(padding_length):
            padding += b'\x00'
        return b''.join([b'\x00\x00',padding,b'\x00',message])
 
    def _encrypt(self, message, pub_key):
        keylength = rsa.common.byte_size(pub_key.n)
        padded = self._pad_for_encryption(message, keylength)
        payload = rsa.transform.bytes2int(padded)
        encrypted = rsa.core.encrypt_int(payload, pub_key.e, pub_key.n)
        block = rsa.transform.int2bytes(encrypted, keylength)
        return block

#pk = "B3C61EBBA4659C4CE3639287EE871F1F48F7930EA977991C7AFE3CC442FEA49643212E7D570C853F368065CC57A2014666DA8AE7D493FD47D171C0D894EEE3ED7F99F6798B7FFD7B5873227038AD23E3197631A8CB642213B9F27D4901AB0D92BFA27542AE890855396ED92775255C977F5C302F1E7ED4B1E369C12CB6B1822F"
#en = Encrypt(pk)
#print(en.encrypt_nopadding("12345678"))