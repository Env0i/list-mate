// 提交前把指定字段的空串归一化为 null。
// 后端 pydantic 的 Optional 数字/状态字段不接受 ""（v-model.number 清空输入框后会得到 ""），
// 直接提交会 422；需要清空的字段应发 null。
export function emptyToNull(obj, keys) {
  const out = { ...obj }
  for (const k of keys) {
    if (out[k] === '') out[k] = null
  }
  return out
}
