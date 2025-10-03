from flask import Flask, jsonify, request
import requests
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from protobuf_decoder.protobuf_decoder import Parser
from datetime import datetime
import json

app = Flask(__name__)

com_garena_msdk_uid = "3942040791"
com_garena_msdk_password = "EDD92B8948F4453F544C9432DFB4996D02B4054379A0EE083D8459737C50800B"
com_jwt_generate_url = "https://100067.vercel.app/token"

def get_jwt():
    try:
        params = {
            'uid': com_garena_msdk_uid,
            'password': com_garena_msdk_password
        }
        response = requests.get(com_jwt_generate_url, params=params)
        if response.status_code == 200:
            jwt_data = response.json()
            return jwt_data.get("token")  
        return None
    except Exception as e:
        print(f"Error fetching JWT: {e}")
        return None
        
def Encrypt_ID(x):
    x = int(x)
    dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    xxx = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    x = x / 128
    if x > 128:
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                m = (n - int(strn)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
            else:
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def parse_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
            result_dict[result.field] = field_data
        elif result.wire_type == "string":
            field_data['data'] = result.data
            result_dict[result.field] = field_data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = parse_results(result.data.results)
            result_dict[result.field] = field_data
    return result_dict

def get_available_room(input_text):
    parsed_results = Parser().parse(input_text)
    parsed_results_dict = parse_results(parsed_results)
    return json.dumps(parsed_results_dict)

@app.route('/')
def index():
    return jsonify({
        "FF Information": [
            {
                "credits": "Ujjaiwal"
            }
        ]
    })

@app.route('/info', methods=['GET'])
def get_player_info():
    try:
        player_id = request.args.get('uid')
        if not player_id:
            return jsonify({
                "Error": [
                    {
                        "message": "Player ID is required"
                    }
                ]
            }), 400

        jwt_token = get_jwt()
        if not jwt_token:
            return jsonify({
                "Error": [
                    {
                        "message": "Failed to fetch JWT token"
                    }
                ]
            }), 500

        data = bytes.fromhex(encrypt_api(f"08{Encrypt_ID(player_id)}1007"))
        url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB50', 
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Authorization': f'Bearer {jwt_token}',
            'Content-Length': '16',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'clientbp.ggblueshark.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            hex_response = binascii.hexlify(response.content).decode('utf-8')
            json_result = get_available_room(hex_response)
            parsed_data = json.loads(json_result)

            try:
                basic_info = parsed_data.get("1", {}).get("data", {})
                profile_info = parsed_data.get("2", {}).get("data", {})
                clan_info = parsed_data.get("6", {}).get("data", {})
                captain_info = parsed_data.get("7", {}).get("data", {})
                pet_info = parsed_data.get("8", {}).get("data", {})
                social_info = parsed_data.get("9", {}).get("data", {}) 
                diamond_cost = parsed_data.get("10", {}).get("data", {})
                credit_score_info = parsed_data.get("11", {}).get("data", {})
                external_icon_info = basic_info.get("49", {}).get("data", {})

                player_data = {
                    "AccountInfo": {
                        "AccountBadgeCnt": basic_info.get("18", {}).get("data", 0),
                        "AccountBadgeId": basic_info.get("19", {}).get("data", 0),
                        "AccountBannerID": basic_info.get("11", {}).get("data", 0),
                        "AccountEXP": basic_info.get("7", {}).get("data", 0),
                        "AccountHasElitePass": basic_info.get("17", {}).get("data", False),
                        "AccountHeadPic": basic_info.get("12", {}).get("data", 0),
                        "AccountID": player_id,
                        "AccountLastLoginAt": str(basic_info.get("24", {}).get("data", 0)),
                        "AccountLevel": basic_info.get("6", {}).get("data", 0),
                        "AccountLiked": basic_info.get("21", {}).get("data", 0),
                        "AccountNickname": basic_info.get("3", {}).get("data", ""),
                        "AccountRank": basic_info.get("14", {}).get("data", 0),
                        "AccountRankingPoints": basic_info.get("15", {}).get("data", 0),
                        "AccountRegion": basic_info.get("5", {}).get("data", ""),
                        "AccountRole": basic_info.get("16", {}).get("data", 0),
                        "AccountSeasonId": basic_info.get("20", {}).get("data", 0),
                        "AccountType": basic_info.get("2", {}).get("data", 0),
                        "CsMaxRank": basic_info.get("36", {}).get("data", 0),
                        "CsRank": basic_info.get("30", {}).get("data", 0),
                        "CsRankingPoints": basic_info.get("31", {}).get("data", 0),
                        "EquippedWeaponSkinShows": basic_info.get("32", {}).get("data", []),
                        "MaxRank": basic_info.get("35", {}).get("data", 0),
                        "title": basic_info.get("48", {}).get("data", 0)
                    },
                    "AccountProfileInfo": {
                        "avatarId": profile_info.get("1", {}).get("data", 0),
                        "clothes": profile_info.get("4", {}).get("data", []),
                        "equipedSkills": profile_info.get("5", {}).get("data", []),
                        "pvePrimaryWeapon": profile_info.get("7", {}).get("data", 0),
                        "endTime": profile_info.get("9", {}).get("data", 0)
                    },
                    "captainBasicInfo": {
                        "accountId": str(captain_info.get("1", {}).get("data", 0)),
                        "accountType": captain_info.get("2", {}).get("data", 0),
                        "badgeCnt": captain_info.get("18", {}).get("data", 0),
                        "badgeId": captain_info.get("19", {}).get("data", 0),
                        "bannerId": captain_info.get("11", {}).get("data", 0),
                        "csMaxRank": captain_info.get("36", {}).get("data", 0),
                        "csRank": captain_info.get("30", {}).get("data", 0),
                        "csRankingPoints": captain_info.get("31", {}).get("data", 0),
                        "exp": captain_info.get("7", {}).get("data", 0),
                        "hasElitePass": captain_info.get("17", {}).get("data", False),
                        "headPic": captain_info.get("12", {}).get("data", 0),
                        "lastLoginAt": str(captain_info.get("24", {}).get("data", 0)),
                        "level": captain_info.get("6", {}).get("data", 0),
                        "liked": captain_info.get("21", {}).get("data", 0),
                        "maxRank": captain_info.get("35", {}).get("data", 0),
                        "nickname": captain_info.get("3", {}).get("data", ""),
                        "rank": captain_info.get("14", {}).get("data", 0),
                        "rankingPoints": captain_info.get("15", {}).get("data", 0),
                        "region": captain_info.get("5", {}).get("data", ""),
                        "role": captain_info.get("16", {}).get("data", 0),
                        "seasonId": captain_info.get("20", {}).get("data", 0),
                        "title": captain_info.get("48", {}).get("data", 0),
                        "weaponSkinShows": captain_info.get("32", {}).get("data", [])
                    },
                    "clanBasicInfo": {
                        "capacity": clan_info.get("5", {}).get("data", 0),
                        "captainId": str(clan_info.get("3", {}).get("data", 0)),
                        "clanId": str(clan_info.get("1", {}).get("data", 0)),
                        "clanLevel": clan_info.get("4", {}).get("data", 0),
                        "clanName": clan_info.get("2", {}).get("data", ""),
                        "memberNum": clan_info.get("6", {}).get("data", 0)
                    },
                    "createAt": str(basic_info.get("44", {}).get("data", 0)),
                    "creditScoreInfo": {
                        "creditScore": credit_score_info.get("1", {}).get("data", 0),
                        "periodicSummaryEndTime": str(credit_score_info.get("8", {}).get("data", 0)),
                        "rewardState": "REWARD_STATE_UNCLAIMED" 
                    },
                    "petInfo": {
                        "exp": pet_info.get("4", {}).get("data", 0),
                        "id": pet_info.get("1", {}).get("data", 0),
                        "isSelected": pet_info.get("5", {}).get("data", False),
                        "level": pet_info.get("3", {}).get("data", 0),
                        "name": pet_info.get("2", {}).get("data", ""),
                        "selectedSkillId": pet_info.get("9", {}).get("data", 0),
                        "skinId": pet_info.get("6", {}).get("data", 0)
                    },
                    "releaseVersion": basic_info.get("50", {}).get("data", ""),
                    "showBrRank": basic_info.get("52", {}).get("data", False),
                    "showCsRank": basic_info.get("53", {}).get("data", False),
                    "socialHighLightsWithBasicInfo": {},
                    "socialInfo": {
                        "accountId": str(social_info.get("1", {}).get("data", 0)),
                        "signature": social_info.get("9", {}).get("data", "")
                    }
                }

                return jsonify(player_data)

            except Exception as e:
                return jsonify({
                    "Error": [
                        {
                            "message": f"Failed to parse player information: {str(e)}"
                        }
                    ]
                }), 500

        return jsonify({
            "Error": [
                {
                    "message": f"API request failed with status code: {response.status_code}"
                }
            ]
        }), response.status_code

    except Exception as e:
        return jsonify({
            "Error": [
                {
                    "message": f"An unexpected error occurred: {str(e)}"
                }
            ]
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)