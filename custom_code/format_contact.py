# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name：   format_phone
  date：     2020/7/2
  Author :    jack
  Description :联系方式格式化，拆分，去重
-------------------------------------------------  
"""
import re
import copy

# 手机号
re_mobile_phone = r"^1[3-9]\d{9}$"
# 类似手机号
re_mobile_phone_like = r"^1[3-9]\d{8,10}$"
# 固话，传真,支持国际区号，区号,分机号，验证
re_fixed_phone = r"^(0?\d{2,3}-?)?(0?\d{2,3}-?)?\d{7,8}(-?\d{1,4})?$"
# 固话，传真,支持国际区号，区号,分机号，提取
re_fixed_phone_extract = r"(0?\d{2,3}-?)?(0?\d{2,3}-?)?\d{7,8}(-?\d{1,4})?"
# 固话，传真，号码，分机号提取，用于比较是否同一个号码
re_fixed_phone_h = r"\d{7,8}(-?\d{1,4})?"
# 固话，传真，区号，号码 提取，用于比较是否同一个号码
re_fixed_phone_q = r"(0?\d{2,3}-?)?\d{7,8}(-?\d{1,4})?"
# 邮箱
re_email = r"^[^(@.)]+@+[^@]+$"
# qq号
re_qq = "^[1-9][\d]{4,10}$"
# 邮箱不充许的字符
re_email_bad = "[`~!#$%^*<>?:""{}#￥%……*——{}|《》？：“”【】、；‘’，。、]"

'''        
    1: "mobile_phone",  # 手机号码
    2: "fixed_phone",  # 固定电话
    3: "email",  # 电子邮件
    4: "fax",  # 传真号码
    5: "qq",  # QQ
    6: "other_contact",  # 其他联系方式
    7: "weixin",  # 微信

'''
contact_type_score = {
    1: 7000,
    2: 6000,
    3: 5000,
    7: 4000,
    5: 3000,
    4: 2000,
    6: 1000
}
# 城市区号对照表
code_city_map = {
    "010": "北京市",
    "021": "上海市",
    "022": "天津市",
    "023": "重庆市",
    "0311": "石家庄市",
    "0312": "保定市",
    "0314": "承德市",
    "0310": "邯郸市",
    "0315": "唐山市",
    "0335": "秦皇岛市",
    "0317": "沧州市",
    "0318": "衡水市",
    "0316": "廊坊市",
    "0319": "邢台市",
    "0313": "张家口市",
    "0351": "太原市",
    "0355": "长治市",
    "0352": "大同市",
    "0356": "晋城市",
    "0354": "晋中市",
    "0357": "临汾市",
    "0358": "吕梁市",
    "0349": "朔州市",
    "0350": "忻州市",
    "0359": "运城市",
    "0353": "阳泉市",
    "0471": "呼和浩特市",
    "0472": "包头市",
    "0476": "赤峰市",
    "0477": "鄂尔多斯市",
    "0470": "呼伦贝尔市",
    "0475": "通辽市",
    "0474": "乌兰察布市",
    "0473": "乌海市",
    "0482": "兴安盟市",
    "024": "沈阳市",
    "0411": "大连市",
    "0412": "鞍山市",
    "0415": "丹东市",
    "0413": "抚顺市",
    "0416": "锦州市",
    "0417": "营口市",
    "0414": "本溪市",
    "0428": "朝阳市",
    "0418": "阜新市",
    "0429": "葫芦岛市",
    "0419": "辽阳市",
    "0427": "盘锦市",
    "0410": "铁岭市",
    "0431": "长春市",
    "0432": "吉林市",
    "0436": "白城市",
    "0439": "白山市",
    "0437": "辽源市",
    "0434": "四平市",
    "0438": "松原市",
    "0435": "通化市",
    "0451": "哈尔滨市",
    "0459": "大庆市",
    "0452": "齐齐哈尔市",
    "0454": "佳木斯市",
    "0457": "大兴安岭市",
    "0456": "黑河市",
    "0468": "鹤岗市",
    "0467": "鸡西市",
    "0453": "牡丹江市",
    "0464": "七台河市",
    "0455": "绥化市",
    "0469": "双鸭山市",
    "0458": "伊春市",
    "025": "南京市",
    "0512": "苏州市",
    "0519": "常州市",
    "0518": "连云港市",
    "0523": "泰州市",
    "0510": "无锡市",
    "0516": "徐州市",
    "0514": "扬州市",
    "0511": "镇江市",
    "0517": "淮安市",
    "0513": "南通市",
    "0527": "宿迁市",
    "0515": "盐城市",
    "0571": "杭州市",
    "0574": "宁波市",
    "0573": "嘉兴市",
    "0575": "绍兴市",
    "0577": "温州市",
    "0580": "舟山市",
    "0572": "湖州市",
    "0579": "金华市",
    "0578": "丽水市",
    "0576": "台州市",
    "0551": "合肥市",
    "0553": "芜湖市",
    "0556": "安庆市",
    "0552": "蚌埠市",
    "0558": "亳州市",
    "0565": "巢湖市",
    "0566": "池州市",
    "0550": "滁州市",
    "0558": "阜阳市",
    "0559": "黄山市",
    "0561": "淮北市",
    "0554": "淮南市",
    "0564": "六安市",
    "0555": "马鞍山市",
    "0557": "宿州市",
    "0562": "铜陵市",
    "0563": "宣城市",
    "0591": "福州市",
    "0592": "厦门市",
    "0595": "泉州市",
    "0597": "龙岩市",
    "0593": "宁德市",
    "0599": "南平市",
    "0594": "莆田市",
    "0598": "三明市",
    "0596": "漳州市",
    "0791": "南昌市",
    "0797": "赣州市",
    "0792": "九江市",
    "0798": "景德镇市",
    "0796": "吉安市",
    "0799": "萍乡市",
    "0793": "上饶市",
    "0790": "新余市",
    "0795": "宜春市",
    "0701": "鹰潭市",
    "0531": "济南市",
    "0532": "青岛市",
    "0631": "威海市",
    "0535": "烟台市",
    "0536": "潍坊市",
    "0538": "泰安市",
    "0543": "滨州市",
    "0534": "德州市",
    "0546": "东营市",
    "0530": "菏泽市",
    "0537": "济宁市",
    "0635": "聊城市",
    "0539": "临沂市",
    "0634": "莱芜市",
    "0633": "日照市",
    "0533": "淄博市",
    "0632": "枣庄市",
    "020": "广州市",
    "0755": "深圳市",
    "0756": "珠海市",
    "0769": "东莞市",
    "0757": "佛山市",
    "0752": "惠州市",
    "0750": "江门市",
    "0760": "中山市",
    "0754": "汕头市",
    "0759": "湛江市",
    "0768": "潮州市",
    "0762": "河源市",
    "0663": "揭阳市",
    "0668": "茂名市",
    "0753": "梅州市",
    "0763": "清远市",
    "0751": "韶关市",
    "0660": "汕尾市",
    "0662": "阳江市",
    "0766": "云浮市",
    "0758": "肇庆市",
    "0898": "海口市",
    "0898": "三亚市",
    "0771": "南宁市",
    "0779": "北海市",
    "0771": "崇左市",
    "0770": "防城港市",
    "0773": "桂林市",
    "0775": "贵港市",
    "0778": "河池市",
    "0774": "贺州市",
    "0772": "柳州市",
    "0772": "来宾市",
    "0777": "钦州市",
    "0775": "玉林市",
    "0774": "梧州市",
    "0371": "郑州市",
    "0379": "洛阳市",
    "0378": "开封市",
    "0374": "许昌市",
    "0372": "安阳市",
    "0375": "平顶山市",
    "0392": "鹤壁市",
    "0391": "焦作市",
    "0391": "济源市",
    "0395": "漯河市",
    "0377": "南阳市",
    "0393": "濮阳市",
    "0398": "三门峡市",
    "0370": "商丘市",
    "0373": "新乡市",
    "0376": "信阳市",
    "0396": "驻马店市",
    "0394": "周口市",
    "027": "武汉市",
    "0710": "襄樊市",
    "0719": "十堰市",
    "0714": "黄石市",
    "0711": "鄂州市",
    "0718": "恩施市",
    "0713": "黄冈市",
    "0716": "荆州市",
    "0724": "荆门市",
    "0722": "随州市",
    "0717": "宜昌市",
    "0728": "天门市",
    "0728": "潜江市",
    "0728": "仙桃市",
    "0712": "孝感市",
    "0715": "咸宁市",
    "0731": "长沙市",
    "0730": "岳阳市",
    "0732": "湘潭市",
    "0736": "常德市",
    "0735": "郴州市",
    "0743": "凤凰市",
    "0734": "衡阳市",
    "0745": "怀化市",
    "0738": "娄底市",
    "0739": "邵阳市",
    "0737": "益阳市",
    "0746": "永州市",
    "0733": "株洲市",
    "0744": "张家界市",
    "028": "成都市",
    "0816": "绵阳市",
    "0832": "资阳市",
    "0827": "巴中市",
    "0838": "德阳市",
    "0818": "达州市",
    "0826": "广安市",
    "0839": "广元市",
    "0833": "乐山市",
    "0830": "泸州市",
    "0833": "眉山市",
    "0832": "内江市",
    "0817": "南充市",
    "0812": "攀枝花市",
    "0825": "遂宁市",
    "0831": "宜宾市",
    "0835": "雅安市",
    "0813": "自贡市",
    "0851": "贵阳市",
    "0853": "安顺市",
    "0857": "毕节市",
    "0856": "铜仁市",
    "0852": "遵义市",
    "0871": "昆明市",
    "0877": "玉溪市",
    "0878": "楚雄市",
    "0872": "大理市",
    "0873": "红河市",
    "0874": "曲靖市",
    "0691": "西双版纳市",
    "0870": "昭通市",
    "0891": "拉萨市",
    "0892": "日喀则市",
    "0983": "山南市",
    "029": "西安市",
    "0915": "安康市",
    "0917": "宝鸡市",
    "0916": "汉中市",
    "0914": "商洛市",
    "0919": "铜川市",
    "0913": "渭南市",
    "0910": "咸阳市",
    "0911": "延安市",
    "0912": "榆林市",
    "0931": "兰州市",
    "0943": "白银市",
    "0932": "定西市",
    "0935": "金昌市",
    "0937": "酒泉市",
    "0939": "陇南市",
    "0930": "临夏市",
    "0933": "平凉市",
    "0930": "庆阳市",
    "0935": "武威市",
    "0938": "天水市",
    "0936": "张掖市",
    "0971": "西宁市",
    "0972": "海东市",
    "0970": "海北市",
    "0974": "海南市",
    "0951": "银川市",
    "0952": "石嘴山市",
    "0953": "吴忠市",
    "0953": "中卫市",
    "0991": "乌鲁木齐市",
    "0901": "塔城市",
    "0902": "哈密市",
    "0903": "和田市",
    "0906": "阿勒泰市",
    "0908": "阿图什市",
    "0909": "博乐市",
    "0990": "克拉玛依市",
    "0992": "奎屯市",
    "0993": "石河子市",
    "0994": "昌吉市",
    "0995": "吐鲁番市",
    "0996": "库尔勒市",
    "0997": "阿克苏市",
    "0998": "喀什市",
    "0999": "伊宁市",
    "0937": "嘉峪关市",
    "0888": "丽江市",
    "0837": "阿坝藏族羌族自治州市",
    "0834": "凉山彝族自治州市",
    "0898": "陵水黎族自治县市",
    "0887": "迪庆藏族自治州市",
    "0875": "保山市",
    "0719": "神农架林区市",
    "0570": "衢州市市",
    "0836": "甘孜藏族自治州市",
    "0876": "文山壮族苗族自治州市",
    "0692": "德宏傣族景颇族自治州市",
    "1853": "澳门特别行政区",
    "1852": "香港特别行政区",
    "1886": "台湾"
}

StringNulls = {"none", "null", "暂无", "暂未提供", "暂未填写", "未知", "不详", "nil", "暂末编辑", "无", "无。", "空", "no", "未公开", "未提供"}
RegNullString = re.compile("^[`~!@#$%^&*()_\-+=<>?:""{}|,.\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘’，。、]$")


# 去除某一个值为val
def set_nil_val_one(val):
    # 去除nil值
    if isinstance(val, str) and (val.lower() in StringNulls or RegNullString.search(val)):
        return ""
    return val


# 拆分
def split_contact(contacts, contact_item):
    re_split = "[\,|\||/]"
    if contact_item.get("contact_type") == 3:
        re_split = "[\,\/\s\|]"
    contact_arr = re.split(re_split, contact_item.get("contact_info"))
    if len(contact_arr) > 1:
        contact_item["status"] = 0
        for contact_arr_item in contact_arr:
            contact_new_item = copy.copy(contact_item)
            contact_new_item["status"] = 1
            contact_new_item["contact_info"] = contact_arr_item
            contacts.append(contact_new_item)
        contact_item["is_split"] = 1


# 猜联系内容的类型
def guess_contact_type(contact_item, contact_info):
    is_mobile_phone = re.findall(re_mobile_phone, contact_info)
    if len(is_mobile_phone) > 0:
        return 1

    if contact_item.get("contact_type", 0) == 1:
        # 可能是错误的手机号
        is_mobile_phone_like = re.findall(re_mobile_phone_like, contact_info)
        if len(is_mobile_phone_like) > 0:
            return 0

    is_re_fixed_phone = re.findall(re_fixed_phone, contact_info)
    # 只对手机号和邮箱里的 固话和传真做处理，qq和微信 也有可能是纯数字，不好区分，暂时不做调整。
    if len(is_re_fixed_phone) > 0 and contact_item.get("contact_type", 0) not in [2, 4] and contact_item.get(
            "contact_type", 0) in [1, 3]:
        return 2

    is_re_email = re.findall(re_email, contact_info)
    if len(is_re_email) > 0:
        return 3

    is_re_qq = re.findall(re_qq, contact_info)
    # qq号暂时也不处理固话、传真
    if len(is_re_qq) > 0 and contact_item.get("contact_type", 0) not in [2, 4]:
        return 5
    # 没猜出来是什么类型
    return 0


# 格式化纯数字
def format_fixed_number(_contact_info):
    gj_len = 0
    gj_heard = ""
    if _contact_info[0:2] == "86":
        gj_len = 2
        gj_heard = "086-"
    if _contact_info[0:3] == "086":
        gj_len = 3
        gj_heard = "086-"
    if _contact_info[gj_len:gj_len + 3] in code_city_map:
        _contact_info = gj_heard + _contact_info[gj_len:gj_len + 3] + "-" + _contact_info[gj_len + 3:]
    elif _contact_info[gj_len:gj_len + 4] in code_city_map:
        _contact_info = gj_heard + _contact_info[gj_len:gj_len + 4] + "-" + _contact_info[gj_len + 4:]
    elif "0" + _contact_info[gj_len:gj_len + 2] in code_city_map:
        _contact_info = gj_heard + "0" + _contact_info[gj_len:gj_len + 2] + "-" + _contact_info[gj_len + 2:]
    elif "0" + _contact_info[gj_len:gj_len + 3] in code_city_map:
        _contact_info = gj_heard + "0" + _contact_info[gj_len:gj_len + 3] + "-" + _contact_info[gj_len + 3:]
    return _contact_info


# 格式化 固话、传真
def format_fixed_phone(contact_item):
    _contact_info = contact_item.get("contact_info")

    if not _contact_info or len(_contact_info) < 7:
        contact_item["contact_info"] = ""
        contact_item["status"] = 0
        return
    _contact_info = re.sub("[^\d]", "-", _contact_info).strip("-")
    only_number = re.findall("^\d{7,20}$", _contact_info)
    # 如果开头有两个或是以上的0
    if len(re.findall("^0{2,}", _contact_info)) > 0:
        _contact_info = re.sub("^0{2,}", "0", _contact_info)
    # 支持国际号，纯数字
    if len(only_number) > 0 and len(_contact_info) > 8:
        _contact_info = format_fixed_number(_contact_info)
    else:
        # 非纯数字
        _info_split = _contact_info.split("-")
        for _index, _val in enumerate(_info_split):
            if not _val:
                continue
            # 如果已到了主号码部分，则退出，因为分机号不需要处理
            if len(_val) > 6 and len(_val) < 9:
                break
            elif len(_val) >= 9:
                # 说明号码主体部分是乱的类似于086-02887443468,86075583632951-806
                _info_split[_index] = format_fixed_number(_val)
                break
            # 区号或是国号小于2位的，直接去掉
            if len(_val) < 2:
                _info_split[_index] = ""
            # 区号或者国别号，补0
            elif len(_val) >= 2 and _val[0] != "0":
                _info_split[_index] = "0" + _val
        # 删除空
        _info_split = [i for i in _info_split if i != '']
        _contact_info = "-".join(_info_split)

    _info_split = _contact_info.split("-")
    # 去除分隔出来的重复部分
    _contact_info = []
    for _info_ in _info_split:
        if _info_ not in _contact_info:
            _contact_info.append(_info_)
    _info_split = _contact_info
    # 去除号码主体部分的重复号码
    for _index, _val in enumerate(_info_split):
        # 主号码部分
        if len(_val) > 6 and _val[0] == "0":
            _qu_1 = _val[0:3]
            if _qu_1 in code_city_map:
                _info_split[_index] = _val[3:]
                break
            _qu_2 = _val[0:4]
            if _qu_2 in code_city_map:
                _info_split[_index] = _val[4:]
                break
    _contact_info = "-".join(_info_split)

    if not _contact_info or len(_contact_info) < 7:
        contact_item["contact_info"] = ""
        contact_item["status"] = 0
        return
    contact_item["contact_info"] = _contact_info


# 格式检查
def norm_contact(contacts, contact_item):
    if contact_item["status"] == 0:
        return
    # 去除一些默认为空的值
    contact_item["contact_info"] = set_nil_val_one(contact_item.get("contact_info"))
    # 联系方式为空的
    if not contact_item.get("contact_info"):
        contact_item["status"] = 0
        return
    if len(contact_item.get("contact_info")) < 4:
        contact_item["status"] = 0
        return

    # 手机号
    if contact_item.get("contact_type") == 1:
        mobile_phone_val = re.search(re_mobile_phone, contact_item.get("contact_info"))
        if not mobile_phone_val:
            # 错误的手机号，删除之
            contact_item["status"] = 0
        else:
            contact_item["contact_info"] = mobile_phone_val.group()
        return
    # 固定电话
    if contact_item.get("contact_type") == 2:
        fixed_phone_val = re.search(re_fixed_phone_extract, contact_item.get("contact_info"))
        if not fixed_phone_val:
            # 错误的固定电话，删除之
            contact_item["status"] = 0
        else:
            contact_item["contact_info"] = fixed_phone_val.group()
        format_fixed_phone(contact_item)
        return
    # 邮箱
    if contact_item.get("contact_type") == 3:
        # 过滤错误的邮箱
        if contact_item.get("contact_info"):
            contact_item["contact_info"] = re.sub(re_email_bad, "", contact_item.get("contact_info"))
        email_val = re.search(re_email, contact_item.get("contact_info"))
        if not email_val:
            # 错误的邮箱，删除之
            contact_item["status"] = 0
        else:
            contact_item["contact_info"] = email_val.group()
        return

    # 传真电话
    if contact_item.get("contact_type") == 4:
        fixed_phone_val = re.search(re_fixed_phone_extract, contact_item.get("contact_info"))
        if not fixed_phone_val:
            # 错误的传真，删除之
            contact_item["status"] = 0
        else:
            contact_item["contact_info"] = fixed_phone_val.group()
        format_fixed_phone(contact_item)
        return

    # 其他联系方式，超长的联系方式删除掉
    if contact_item.get("contact_type") == 6:
        if len(contact_item.get("contact_info")) > 64:
            # 错误的传真，删除之
            contact_item["status"] = 0
        return

    # qq
    if contact_item.get("contact_type") == 5:
        qq_val = re.search(re_qq, contact_item.get("contact_info"))
        if not qq_val:
            # 错误的邮箱，删除之
            contact_item["status"] = 0
        else:
            contact_item["contact_info"] = qq_val.group()
        return
    # weixin
    if contact_item.get("contact_type") == 7:
        if len(contact_item.get("contact_info")) < 5:
            # 微信号，长度小于5位数则删除
            contact_item["status"] = 0
        return


# 空号过滤，别高兴太早，只过滤全是0，或是1234567这种
def filter_empty(contact_item):
    if contact_item.get("contact_type") not in [1, 2, 4]:
        return
    _contact_info = contact_item.get("contact_info")
    if len(re.findall("0{7,}", _contact_info)) > 0:
        contact_item["status"] = 0
    elif len(re.findall(r"123456|1234567|12345678", _contact_info)) > 0:
        contact_item["status"] = 0
    # 好到怀疑人生的靓号，肯定是假的
    elif len(re.findall(r"(\d)\1{6,}", _contact_info)) > 0:
        contact_item["status"] = 0
    elif not _contact_info:
        contact_item["status"] = 0


# 删除重复数据
def duplicate_contact(contacts, del_contact_infos):
    if not contacts:
        return contacts
    contacts_exists = {}
    new_contacts = []
    for contact in contacts:
        if contact.get("status") == 0:
            continue
        if not contact.get("contact_person"):
            contact["contact_person"] = ""
        if not contact.get("contact_position"):
            contact["contact_position"] = ""
        if not contact.get("contact_type"):
            contact["contact_type"] = ""
        if not contact.get("contact_info"):
            contact["contact_info"] = ""
        contact_info = contact.get("contact_info")
        contact_info_key = str(contact.get(
            "contact_type")) + "|" + contact_info  # 以前的版本有多个关键字 + "-" + contact.get("contact_person") + "-" + contact.get("contact_position")
        # 如果是固定电话，解析号码部分
        if contact.get("contact_type") in [2, 4]:
            _contact_info_search = re.search(re_fixed_phone_h, contact_info)
            if _contact_info_search:
                contact_info_key = str(contact.get(
                    "contact_type")) + "|" + _contact_info_search.group()

        if contact_info_key not in contacts_exists.keys():
            contacts_exists[contact_info_key] = {"contact_person": contact.get("contact_person"),
                                                 "contact_position": contact.get("contact_position"),
                                                 "contact_type": contact.get("contact_type"),
                                                 "contact_info": contact_info,
                                                 }


        else:

            if contact.get("contact_type") in [2, 4]:
                # 号码相同，区号不同
                _contacts_exists_q_t = re.search(re_fixed_phone_q,
                                                 contacts_exists[contact_info_key].get("contact_info"))
                _contact_q_t = re.search(re_fixed_phone_q, contact.get("contact_info"))
                if _contacts_exists_q_t and _contact_q_t:
                    _contacts_exists_qh = re.search("(0?\d{2,3})-", _contacts_exists_q_t.group())
                    _contact_qh = re.search("(0?\d{2,3})-", _contact_q_t.group())
                    if _contacts_exists_qh and _contact_qh and _contacts_exists_qh.group() != _contact_qh.group():
                        contact_info_key = str(contact.get(
                            "contact_type")) + "|" + contact_info
                        if contact_info_key not in contacts_exists.keys():
                            contacts_exists[contact_info_key] = {"contact_person": contact.get("contact_person"),
                                                                 "contact_position": contact.get("contact_position"),
                                                                 "contact_type": contact.get("contact_type"),
                                                                 "contact_info": contact_info,

                                                                 }
                            continue
            # 号码相同，区号不同
            _contact_person = contacts_exists[contact_info_key].get("contact_person")
            _contact_position = contacts_exists[contact_info_key].get("contact_position")
            _contact_type = contacts_exists[contact_info_key].get("contact_type")
            _contact_info = contacts_exists[contact_info_key].get("contact_info")
            _contact_info_org = _contact_info

            if not _contact_info and contact.get("contact_info"):
                _contact_info = contact.get("contact_info")
            elif _contact_info and contact.get("contact_info") and len(contact.get("contact_info")) > len(
                    _contact_info):
                _contact_info = contact.get("contact_info")

            # 记录哪些联系是被删除了的
            if _contact_info_org != _contact_info:
                del_contact_info = contacts_exists[contact_info_key]
            else:
                del_contact_info = contact
            del_contact_info["is_duplicate"] = True
            del_contact_infos.append(del_contact_info)
            contacts_exists[contact_info_key] = {"contact_person": _contact_person,
                                                 "contact_position": _contact_position,
                                                 "contact_type": _contact_type,
                                                 "contact_info": _contact_info,

                                                 }

    for contact_info_key in contacts_exists.keys():
        new_contacts.append(contacts_exists.get(contact_info_key))
    return new_contacts


# 格式化联系人
def format_person(contacts, contact_item):
    if not contact_item.get("contact_person") or not isinstance(contact_item.get("contact_person"), str):
        contact_item["contact_person"] = ""
        return
    contact_item["contact_person"] = re.sub("\(\)|\{\}|\[\]|（）", "", contact_item.get("contact_person"))
    contact_item["contact_person"] = re.sub("^[0-9]*$", "", contact_item.get("contact_person"))
    contact_item["contact_person"] = set_nil_val_one(contact_item["contact_person"])
    # 因为爬虫部分网站没搞对，所以把有|线，并且字符长度大于20的数据隐藏
    if contact_item.get("contact_person") and "|" in contact_item.get("contact_person") and len(
            contact_item.get("contact_person")) > 20:
        contact_item["contact_person"] = ""


# 格式化职位
def format_position(contacts, contact_item):
    if not contact_item.get("contact_position") or not isinstance(contact_item.get("contact_position"), str):
        contact_item["contact_position"] = ""
        return


# 联系信息格式化
def format_contact(contacts):
    if not contacts:
        return
    for contact_item in contacts:
        # 增加是否删除标记 0:删除 1 :正常 不要直接删除，for会有问题。后面统一处理
        contact_item["status"] = 1
        if not contact_item["contact_info"]:
            contact_item["status"] = 0
            continue

        contact_item["contact_info"] = contact_item.get("contact_info").strip().lower()
        split_contact(contacts, contact_item)
        # 格式化联系人
        format_person(contacts, contact_item)
        # 格式化职位
        format_position(contacts, contact_item)
        # 矫正联系方式类型
        contact_type = guess_contact_type(contact_item, contact_item.get("contact_info"))
        if contact_type > 0:
            contact_item["contact_type"] = contact_type
        # 统一格式固定电话分隔符
        if contact_item.get("contact_type", 0) in [2, 4] and contact_item["status"] == 1:
            contact_item["contact_info"] = re.sub("[^\d]", "-", contact_item["contact_info"]).strip("-")

        norm_contact(contacts, contact_item)
        filter_empty(contact_item)

        # 再做一次类型修改 矫正联系方式类型
        contact_type = guess_contact_type(contact_item, contact_item.get("contact_info"))
        if contact_type > 0:
            contact_item["contact_type"] = contact_type

    # 真实删除,为什么不在上面删？因为要出错。
    length = len(contacts)
    del_contact_infos = []
    while length > 0:
        length -= 1
        if contacts[length].get("status") == 0:
            del_contact_infos.append(copy.deepcopy(contacts[length]))
            contacts.pop(length)

    # 去重
    new_contacts = duplicate_contact(contacts, del_contact_infos)

    return new_contacts, del_contact_infos


if __name__ == "__main__":
    contacts = [
        {
            "contact_person": "张三",
            "contact_position": "厂长",
            "contact_type": 2,
            "contact_info": "18280284156",

        }, {
            "contact_person": "张三",
            "contact_position": "厂长",
            "contact_type": 5,
            "contact_info": "10207242999",

        }, {
            "contact_person": "张三(001)",
            "contact_position": "厂长",
            "contact_type": 1,
            "contact_info": "18280100000,18280100003",

        }, {
            "contact_person": "李四",
            "contact_position": "厂长",
            "contact_type": 1,
            "contact_info": "18280100001",
        }, {
            "contact_person": "王强",
            "contact_position": "联系人",
            "contact_type": 3,
            "contact_info": "41700001@qq.com",
        }
        ,
        {
            "contact_person": "王强",
            "contact_position": "坐机",
            "contact_type": 2,
            "contact_info": "02887443408-01",
        }
        ,
        {
            "contact_person": "王强",
            "contact_position": "坐机",
            "contact_type": 1,
            "contact_info": "02887443408(01)",
        },
        {
            "contact_person": "王强",
            "contact_position": "坐机",
            "contact_type": 1,
            "contact_info": "02887443409,02887443408(01)",
        }
    ]
    new_contacts, del_contact_infos = format_contact(contacts)
    print(new_contacts, del_contact_infos)
