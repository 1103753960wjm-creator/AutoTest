from fastapi import Query
import base64
import hashlib
from urllib.parse import quote, unquote

async def encrypt_md5(data: str):
    """
    将字符串进行MD5加密
    """
    hash_md5 = hashlib.md5()
    hash_md5.update(data.encode("utf-8"))
    md5_data = hash_md5.hexdigest()
    return md5_data

async def encrypt_base64(data: str):
    """
    将字符串进行base64加密
    """
    base64_result = base64.b64encode(data.encode('utf-8')).decode(encoding='utf-8')
    return base64_result

async def decode_base64(data: str) -> bytes:
    """
    将字符串进行base64解码
    """
    decoded_data = base64.b64decode(data)
    return decoded_data

# Unicode编码
async def unicode_encode(text: str = Query(..., description="需要编码的字符串")):
    """
    将字符串转换为Unicode编码
    """
    encoded_text = "".join([f"\\u{ord(char):04x}" for char in text])
    return {"original_text": text, "encoded_text": encoded_text}

# Unicode解码
async def unicode_decode(encoded_text: str = Query(..., description="需要解码的Unicode字符串")):
    """
    将Unicode编码转换回字符串
    """
    try:
        # 将形如 "\u4f60\u597d" 的字符串解码
        decoded_text = encoded_text.encode('utf-8').decode('unicode_escape')
        return {"encoded_text": encoded_text, "decoded_text": decoded_text}
    except Exception as e:
        return {"error": f"解码失败: {str(e)}"}

# URL编码
async def url_encode(text: str = Query(..., description="需要URL编码的字符串")):
    """
    将字符串转换为URL编码格式
    """
    encoded_text = quote(text)
    return {"original_text": text, "encoded_text": encoded_text}

# URL解码
async def url_decode(encoded_text: str = Query(..., description="需要URL解码的字符串")):
    """
    将URL编码转换回原始字符串
    """
    decoded_text = unquote(encoded_text)
    return {"encoded_text": encoded_text, "decoded_text": decoded_text}