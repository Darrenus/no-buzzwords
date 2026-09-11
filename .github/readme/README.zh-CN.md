<p align="center">
  <strong>说人话的技术解释。该留的术语留着，撑场面的词删掉。</strong>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/Darrenus/no-buzzwords?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="../../README.md" title="English" aria-label="English">🇬🇧</a> ·
  <strong title="简体中文" aria-label="简体中文">🇨🇳</strong>
</p>

## 它做什么

一个给编程助手用的 skill，专治它把解释往华丽里写。它会直接说到底发生了什么，而不是甩一个模式的名字；会用「用」而不是「赋能」「利用」；会把「健壮、可扩展」换成一个具体数字。

它不是精简插件。说人话的解释经常比黑话版更长——因为它要补上黑话跳过的那部分活。

## 前后对比

<table>
<tr>
<td width="50%">

### 改之前

> 该服务采用事件驱动架构，借助消息中间件实现限界上下文之间的松耦合，从而获得健壮且可水平扩展的拓扑结构，运维开销极低。消费端应设计为幂等，以应对至少一次投递语义。

</td>
<td width="50%">

### 改之后

> 下单的时候，API 往 RabbitMQ 的一个队列里写一行。shipping 服务按自己的节奏去读这个队列。两个服务谁都不调用谁，所以其中一个挂一阵子，另一个照常跑。
>
> RabbitMQ 有可能把同一条消息投给你两次，所以 shipping 服务必须是幂等的——跑两遍和跑一遍的结果一样。具体做法：写入时拿 `order_id` 当键，第二次跑就是覆盖而不是又插一条。
>
> 单个 worker 大概每分钟处理 2000 条。超过这个量就加 worker。

</td>
</tr>
</table>

第二版更长。但只有第二版你能照着动手。

## 十条规则

完整正文在 [SKILL.md](../../skills/no-buzzwords/SKILL.md)（英文）。

1. 说机制，不要说类别。
2. 用平实的动词，别用唬人的动词。
3. 删掉没人会宣称反面的形容词。
4. 把名词短语还原成动词。
5. 术语第一次出现时解释一次，之后不再解释。
6. 每个抽象说法后面跟一个具体例子。
7. 精度本身就是重点时，保留准确的术语。
8. 比喻放在机制后面，绝不用来顶替机制。
9. 说具体的那个东西，别说它属于哪个类别。
10. 不要用黑话掩盖自己不知道。

## 撑着这十条的那个检验

> 一个从没见过这个子系统的合格工程师，能不能用自己的话把你的解释复述一遍，而且是对的？

不能，那这句话就还没说成人话。

## 安装

```bash
claude plugin marketplace add Darrenus/no-buzzwords
claude plugin install no-buzzwords@no-buzzwords
```

装完在会话里打 `/no-buzzwords`。一直生效，直到你说「stop no-buzzwords」。

其他运行时和手动安装方式见 [INSTALL.md](../../INSTALL.md)（英文）。

## 常驻开启（可选）

默认是手动开的——风格选择本来就该由你决定。想让它从每个会话的第一条消息就生效：

```bash
touch ~/.claude/.no-buzzwords-always
```

删掉这个文件就退回手动模式。

## 它不做什么

- **不禁止技术术语。** `幂等`、`竞态条件`、`TCP 握手` 是特定事物的准确名字，规则 5 的做法是让助手为这些词付一次解释的成本，而不是把它们删掉。
- **不给标识符改名。** 一个叫 `serialize` 的函数，还是叫 `serialize`。
- **不简化那些精度带责任的文本**：许可证条款、药物剂量、安全边界。
- **不负责把回答变短。** 那是另一个问题，[i-have-adhd](https://github.com/ayghri/i-have-adhd) 已经解决了。两个可以叠着用。

## 来源

结构和打包方式参考了 [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)，那个插件管的是回答的形状。这里的规则管的是用词和抽象层级。

## 许可

MIT
