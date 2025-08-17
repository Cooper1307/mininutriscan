档中心>文字识别>服务端 API 文档>通用文字识别相关接口>通用印刷体识别
通用印刷体识别
最近更新时间：2025-08-01 15:38:11

我的收藏
本页目录：
1. 接口描述
2. 输入参数
3. 输出参数
4. 示例
示例1 GeneralBasicOCR调用
5. 开发者资源
腾讯云 API 平台
API Inspector
SDK
命令行工具
6. 错误码
1. 接口描述
接口请求域名： ocr.tencentcloudapi.com 。

本接口支持图像整体文字的检测和识别。可以识别中文、英文、中英文、日语、韩语、西班牙语、法语、德语、葡萄牙语、越南语、马来语、俄语、意大利语、荷兰语、瑞典语、芬兰语、丹麦语、挪威语、匈牙利语、泰语，阿拉伯语20种语言，且各种语言均支持与英文混合的文字识别。

适用于印刷文档识别、网络图片识别、广告图文字识别、街景店招牌识别、菜单识别、视频标题识别、头像文字识别等场景。

产品优势：支持自动识别语言类型，可返回文本框坐标信息，对于倾斜文本支持自动旋转纠正。

通用印刷体识别不同版本的差异如下：

【荐】通用印刷体识别	【荐】通用印刷体识别（高精度版）	通用印刷体识别（精简版）
适用场景	适用于所有通用场景的印刷体识别	适用于文字较多、长串数字、小字、模糊字、倾斜文本等困难场景	适用于快速文本识别场景，准召率有一定损失，价格更优惠
识别准确率	96%	99%	91%
价格	中	高	低
支持的语言	中文、英文、中英文、日语、韩语、西班牙语、法语、德语、葡萄牙语、越南语、马来语、俄语、意大利语、荷兰语、瑞典语、芬兰语、丹麦语、挪威语、匈牙利语、泰语	中文、英文、中英文	中文、英文、中英文
自动语言检测	支持	支持	支持
返回文本行坐标	支持	支持	支持
自动旋转纠正	支持旋转识别，返回角度信息	支持旋转识别，返回角度信息	支持旋转识别，返回角度信息
默认接口请求频率限制：20次/秒。

推荐使用 API Explorer
点击调试
API Explorer 提供了在线调用、签名验证、SDK 代码生成和快速检索接口等能力。您可查看每次调用的请求内容和返回结果以及自动生成 SDK 调用示例。
2. 输入参数
以下请求参数列表仅列出了接口请求参数和部分公共参数，完整公共参数列表见 公共请求参数。

参数名称	必选	类型	描述
Action	是	String	公共参数，本接口取值：GeneralBasicOCR。
Version	是	String	公共参数，本接口取值：2018-11-19。
Region	否	String	公共参数，此参数为可选参数。
ImageBase64	否	String	图片/PDF的 Base64 值。要求图片/PDF经Base64编码后不超过 10M，分辨率建议600*800以上，支持PNG、JPG、JPEG、BMP、PDF格式。图片的 ImageUrl、ImageBase64 必须提供一个，如果都提供，只使用 ImageUrl。
示例值：/9j/4AAQSkZJRg.....s97n//2Q==
ImageUrl	否	String	图片/PDF的 Url 地址。要求图片/PDF经Base64编码后不超过 10M，分辨率建议600*800以上，支持PNG、JPG、JPEG、BMP、PDF格式。图片下载时间不超过 3 秒。图片存储于腾讯云的 Url 可保障更高的下载速度和稳定性，建议图片存储于腾讯云。非腾讯云存储的 Url 速度和稳定性可能受一定影响。
示例值：https://ocr-demo-1254418846.cos.ap-guangzhou.myqcloud.com/general/GeneralBasicOCR/GeneralBasicOCR1.jpg
Scene	否	String	保留字段。
LanguageType	否	String	识别语言类型。
支持自动识别语言类型，同时支持自选语言种类，默认中英文混合(zh)，各种语言均支持与英文混合的文字识别。
可选值：
zh：中英混合
zh_rare：支持英文、数字、中文生僻字、繁体字，特殊符号等
auto：自动
mix：多语言混排场景中,自动识别混合语言的文本
jap：日语
kor：韩语
spa：西班牙语
fre：法语
ger：德语
por：葡萄牙语
vie：越语
may：马来语
rus：俄语
ita：意大利语
hol：荷兰语
swe：瑞典语
fin：芬兰语
dan：丹麦语
nor：挪威语
hun：匈牙利语
tha：泰语
hi：印地语
ara：阿拉伯语
示例值：zh
IsPdf	否	Boolean	是否开启PDF识别，默认值为false，开启后可同时支持图片和PDF的识别。
示例值：true
PdfPageNumber	否	Integer	需要识别的PDF页面的对应页码，仅支持PDF单页识别，当上传文件为PDF且IsPdf参数值为true时有效，默认值为1。
示例值：1
IsWords	否	Boolean	是否返回单字信息，默认关
示例值：false
3. 输出参数
参数名称	类型	描述
TextDetections	Array of TextDetection	检测到的文本信息，包括文本行内容、置信度、文本行坐标以及文本行旋转纠正后的坐标，具体内容请点击左侧链接。
Language	String	检测到的语言类型，目前支持的语言类型参考入参LanguageType说明。
示例值：zh
PdfPageSize	Integer	图片为PDF时，返回PDF的总页数，默认为0
示例值：0
Angle	Float	图片旋转角度（角度制），文本的水平方向为0°；顺时针为正，逆时针为负。点击查看如何纠正倾斜文本
示例值：6.5
RequestId	String	唯一请求 ID，由服务端生成，每次请求都会返回（若请求因其他原因未能抵达服务端，则该次请求不会获得 RequestId）。定位问题时需要提供该次请求的 RequestId。
4. 示例
示例1 GeneralBasicOCR调用
识别多场景、任意版面下整图文字的识别 前往调试工具

输入示例
POST / HTTP/1.1
Host: ocr.tencentcloudapi.com
Content-Type: application/json
X-TC-Action: GeneralBasicOCR
<公共请求参数>

{
    "ImageUrl": "https://ocr-demo-1254418846.cos.ap-guangzhou.myqcloud.com/general/GeneralBasicOCR/GeneralBasicOCR1.jpg"
}
输出示例
{
    "Response": {
        "Angle": 359.989990234375,
        "Language": "zh",
        "PdfPageSize": 0,
        "RequestId": "5d5fbda3-3f47-45a7-8d4b-71bd9d64ab3d",
        "TextDetections": [
            {
                "AdvancedInfo": "{\"Parag\":{\"ParagNo\":1}}",
                "Confidence": 100,
                "DetectedText": "Sun",
                "ItemPolygon": {
                    "Height": 35,
                    "Width": 74,
                    "X": 464,
                    "Y": 100
                },
                "Polygon": [
                    {
                        "X": 464,
                        "Y": 100
                    },
                    {
                        "X": 538,
                        "Y": 100
                    },
                    {
                        "X": 538,
                        "Y": 135
                    },
                    {
                        "X": 464,
                        "Y": 135
                    }
                ],
                "WordCoordPoint": [],
                "Words": []
            },
            {
                "AdvancedInfo": "{\"Parag\":{\"ParagNo\":2}}",
                "Confidence": 100,
                "DetectedText": "1月8日",
                "ItemPolygon": {
                    "Height": 18,
                    "Width": 52,
                    "X": 476,
                    "Y": 141
                },
                "Polygon": [
                    {
                        "X": 476,
                        "Y": 141
                    },
                    {
                        "X": 528,
                        "Y": 141
                    },
                    {
                        "X": 528,
                        "Y": 159
                    },
                    {
                        "X": 476,
                        "Y": 159
                    }
                ],
                "WordCoordPoint": [],
                "Words": []
            },
            {
                "AdvancedInfo": "{\"Parag\":{\"ParagNo\":3}}",
                "Confidence": 100,
                "DetectedText": "八色鸫",
                "ItemPolygon": {
                    "Height": 28,
                    "Width": 85,
                    "X": 62,
                    "Y": 443
                },
                "Polygon": [
                    {
                        "X": 62,
                        "Y": 443
                    },
                    {
                        "X": 147,
                        "Y": 442
                    },
                    {
                        "X": 147,
                        "Y": 470
                    },
                    {
                        "X": 63,
                        "Y": 471
                    }
                ],
                "WordCoordPoint": [],
                "Words": []
            },
            {
                "AdvancedInfo": "{\"Parag\":{\"ParagNo\":4}}",
                "Confidence": 100,
                "DetectedText": "Pitta nympha",
                "ItemPolygon": {
                    "Height": 17,
                    "Width": 96,
                    "X": 61,
                    "Y": 482
                },
                "Polygon": [
                    {
                        "X": 61,
                        "Y": 482
                    },
                    {
                        "X": 157,
                        "Y": 483
                    },
                    {
                        "X": 157,
                        "Y": 500
                    },
                    {
                        "X": 61,
                        "Y": 499
                    }
                ],
                "WordCoordPoint": [],
                "Words": []
            },
            {
                "AdvancedInfo": "{\"Parag\":{\"ParagNo\":5}}",
                "Confidence": 100,
                "DetectedText": "八色鸫雌鸟和雄鸟一样漂亮。它经常在亚热带的森林地面上走动,捕",
                "ItemPolygon": {
                    "Height": 18,
                    "Width": 426,
                    "X": 60,
                    "Y": 506
                },
                "Polygon": [
                    {
                        "X": 60,
                        "Y": 506
                    },
                    {
                        "X": 486,
                        "Y": 503
                    },
                    {
                        "X": 486,
                        "Y": 521
                    },
                    {
                        "X": 60,
                        "Y": 523
                    }
                ],
                "WordCoordPoint": [],
                "Words": []
            },
            {
                "AdvancedInfo": "{\"Parag\":{\"ParagNo\":5}}",
                "Confidence": 100,
                "DetectedText": "食落叶下的昆虫和晰蜴等小动物,唱歌时会飞到树上。因为森林砍伐",
                "ItemPolygon": {
                    "Height": 16,
                    "Width": 426,
                    "X": 60,
                    "Y": 530
                },
                "Polygon": [
                    {
                        "X": 60,
                        "Y": 530
                    },
                    {
                        "X": 486,
                        "Y": 530
                    },
                    {
                        "X": 486,
                        "Y": 546
                    },
                    {
                        "X": 60,
                        "Y": 546
                    }
                ],
                "WordCoordPoint": [],
                "Words": []
            },
            {
                "AdvancedInfo": "{\"Parag\":{\"ParagNo\":5}}",
                "Confidence": 100,
                "DetectedText": "和非法的玩赏鸟贸易,现在它的数量已明显减少。",
                "ItemPolygon": {
                    "Height": 18,
                    "Width": 308,
                    "X": 59,
                    "Y": 554
                },
                "Polygon": [
                    {
                        "X": 59,
                        "Y": 554
                    },
                    {
                        "X": 367,
                        "Y": 552
                    },
                    {
                        "X": 368,
                        "Y": 570
                    },
                    {
                        "X": 59,
                        "Y": 572
                    }
                ],
                "WordCoordPoint": [],
                "Words": []
            }
        ]
    }
}
5. 开发者资源
腾讯云 API 平台
腾讯云 API 平台 是综合 API 文档、错误码、API Explorer 及 SDK 等资源的统一查询平台，方便您从同一入口查询及使用腾讯云提供的所有 API 服务。

API Inspector
用户可通过 API Inspector 查看控制台每一步操作关联的 API 调用情况，并自动生成各语言版本的 API 代码，也可前往 API Explorer 进行在线调试。

SDK
云 API 3.0 提供了配套的开发工具集（SDK），支持多种编程语言，能更方便的调用 API。

Tencent Cloud SDK 3.0 for Python: GitHub, Gitee
Tencent Cloud SDK 3.0 for Java: GitHub, Gitee
Tencent Cloud SDK 3.0 for PHP: GitHub, Gitee
Tencent Cloud SDK 3.0 for Go: GitHub, Gitee
Tencent Cloud SDK 3.0 for Node.js: GitHub, Gitee
Tencent Cloud SDK 3.0 for .NET: GitHub, Gitee
Tencent Cloud SDK 3.0 for C++: GitHub, Gitee
Tencent Cloud SDK 3.0 for Ruby: GitHub, Gitee
命令行工具
Tencent Cloud CLI 3.0
6. 错误码
以下仅列出了接口业务逻辑相关的错误码，其他错误码详见 公共错误码。

错误码	描述
FailedOperation.DownLoadError	文件下载失败。
FailedOperation.EmptyImageError	图片内容为空。
FailedOperation.EngineRecognizeTimeout	引擎识别超时。
FailedOperation.ImageDecodeFailed	图片解码失败。
FailedOperation.ImageNoText	图片中未检测到文本。
FailedOperation.LanguageNotSupport	输入的Language不支持。
FailedOperation.OcrFailed	OCR识别失败。
FailedOperation.UnKnowError	未知错误。
FailedOperation.UnOpenError	服务未开通。
InvalidParameterValue.InvalidParameterValueLimit	参数值错误。
LimitExceeded.TooLargeFileError	文件内容太大。
ResourceUnavailable.InArrears	账号已欠费。
ResourcesSoldOut.ChargeStatusException	计费状态异常。