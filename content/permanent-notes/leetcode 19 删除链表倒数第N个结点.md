---
title: 'leetcode 19 删除链表倒数第N个结点'
created: 'September 10, 2022 2:07 PM'
modified: 'September 20, 2022 10:30 AM'
type: 'CS'
tags:
  - 'Algorithm'
  - 'JavaScript'
---

双指针, 当一个指针A走了N步, 剩下的步数就是 length-N. 这时添加第二个指针B在开头, A走到结尾, B就找到第N个节点;
找到节点后, 删除就很简单了;
