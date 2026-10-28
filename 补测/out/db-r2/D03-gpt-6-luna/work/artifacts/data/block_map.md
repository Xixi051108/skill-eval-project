# 数据块映射

- 版本与场景顺序：来自 `data/iter.json` 的 `meta.products`、`meta.scenarios`。
- 版本曲线与峰值：来自 `records` 中各版本、场景的 QPS；每场景取 QPS 最大值。
- 回退检测：按相邻来源版本比较峰值 QPS，跌幅严格大于 5% 标记。
- 延迟趋势：各版本峰值 QPS 对应记录的 P95。
