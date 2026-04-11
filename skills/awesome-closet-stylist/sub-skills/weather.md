# weather

天气查询规约。当穿搭推荐或用户问询需要实时天气数据时，遵循本规约获取天气信息。

---

## 触发条件

以下情况需要查询天气：
- 用户提到"今天/明天天气"、具体温度、天气状况
- 用户未说明天气，但推荐结果会因天气明显不同（如保暖层、防风防雨需求）
- 用户明确要求基于当前天气做推荐

如果用户已在对话中提供了足够的天气信息（如"今天 18 度有点风"），优先使用用户提供的信息，不必查询 API。

---

## 用户配置

天气 API 配置默认存放于 `user/config.json`，schema 示例：

```json
{
  "weather_apis": [
    { "provider": "amap", "key": "YOUR_KEY_HERE" },
    { "provider": "qweather", "key": "YOUR_KEY_HERE" }
  ],
  "default_city": "上海"
}
```

读取配置时：
- 若 `weather_apis` 列表为空或文件不存在，视为"未配置 API"，进入无 API 分支
- 若 `default_city` 有值，查询时优先使用；否则询问用户城市
- 当用户尚未配置 API 时，优先建议用户填写 API key，并明确说明这些配置只保存在本地
- 可优先推荐配置更简单的天气服务（如和风天气）；如果用户觉得配置麻烦，再退回浏览器搜索天气的兜底方案

---

## 查询流程

### 分支一：已配置 API

读取 `user/config.json` 中的 `weather_apis` 列表，对列表中每个 API **平级尝试**（无优先级，按顺序逐个调用，首个成功即用）。

**支持的 provider 及调用方式：**

#### `amap`（高德天气）
- Endpoint：`https://restapi.amap.com/v3/weather/weatherInfo`
- 参数：`key`、`city`（adcode 或城市名）、`extensions=base`、`output=JSON`

```bash
# bash
curl "https://restapi.amap.com/v3/weather/weatherInfo?key={KEY}&city={CITY}&extensions=base&output=JSON"
```

```powershell
# PowerShell
Invoke-RestMethod "https://restapi.amap.com/v3/weather/weatherInfo?key={KEY}&city={CITY}&extensions=base&output=JSON"
```

解析字段：`lives[0].temperature`、`lives[0].weather`、`lives[0].winddirection`、`lives[0].windpower`、`lives[0].humidity`

#### `qweather`（和风天气）
- Endpoint：`https://devapi.qweather.com/v7/weather/now`
- 参数：`key`、`location`（城市名或 LocationID）

```bash
# bash
curl "https://devapi.qweather.com/v7/weather/now?key={KEY}&location={CITY}"
```

```powershell
# PowerShell
Invoke-RestMethod "https://devapi.qweather.com/v7/weather/now?key={KEY}&location={CITY}"
```

解析字段：`now.temp`、`now.text`、`now.windDir`、`now.windScale`、`now.humidity`

---

若列表中所有 API 均失败，降级进入**分支二**。

---

### 分支二：未配置 API（或所有 API 失败）

通过浏览器获取天气，步骤：

1. 若不知道用户城市，先询问城市
2. 用浏览器访问 `https://www.weather.com.cn/` 或搜索 `{城市} 今日天气`，从页面提取温度和天气状况
3. 提取后直接用于推荐，不向用户播报"我查到天气了"

---

### 分支三：浏览器也无法获取

向用户说明：
> "我现在无法自动获取天气数据，请告诉我今天大概的温度和天气状况，我根据你提供的信息来帮你搭配。"

---

## 无 API 时的主动建议

当检测到 `user/config.json` 不存在或 `weather_apis` 为空时，在本次回复中附带一条轻量提示（每次 session 只提示一次）：

> "目前没有配置天气 API。更推荐你在 `user/config.json` 里填写 key，这样更稳定，而且数据只保存在本地；如果你想省事，我也可以直接通过浏览器获取天气。若要推荐一个最省事的服务，优先考虑和风天气：https://dev.qweather.com/ 。"

---

## 天气数据的使用方式

获取天气数据后：
- 将温度、天气状况、风力转化为穿搭判断维度（保暖需求、防风防雨需求）
- 在推荐理由中自然融入天气因素，如"今天 12 度有风，加了这件毛呢外套会舒服很多"
- 不向用户复述 API 原始响应，不单独播报"我已查询天气"
