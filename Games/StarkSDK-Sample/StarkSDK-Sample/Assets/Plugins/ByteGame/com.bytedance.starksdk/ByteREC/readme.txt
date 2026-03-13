# 2021-07-08 Unity VERSION = 8
- 修复切后台音频补帧逻辑异常问题（切后台场景不需要做补帧)

# 2021-07-02 Unity VERSION = 7
- 传递ColorSpace给Native解决LinearSpace下渲染颜色异常问题
- 解决URP下录制时候游戏画面刷新问题

# 2021-06-17 Unity VERSION = 6
- 移除部分冗余逻辑
- 增加异常日志
- 支持将关键日志通过SendLogInfo抛给Native做后续上报
- 支持将录制相关参数通过调用Native的startRecordV2带给Native
