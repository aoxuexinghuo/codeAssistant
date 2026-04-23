export const learningTopics = [
  {
    slug: 'c-language',
    title: 'C语言',
    level: '基础语言',
    desc: '适合打牢底层编程基础，理解内存、指针、过程式编程和系统级思维。',
    summary: '如果你想补足计算机基础，C语言是很好的起点，尤其适合理解内存和程序执行方式。',
    audience: ['适合编程初学者', '适合准备学习数据结构、操作系统或嵌入式的人'],
    focus: ['基础语法', '指针与数组', '函数与文件组织', '内存与输入输出'],
    links: [
      {
        label: 'C reference on cppreference',
        url: 'https://en.cppreference.com/w/c/language.html',
        source: 'cppreference',
      },
      {
        label: 'C library reference on cppreference',
        url: 'https://en.cppreference.com/w/c.html',
        source: 'cppreference',
      },
    ],
  },
  {
    slug: 'java',
    title: 'Java',
    level: '工程语言',
    desc: '适合系统学习面向对象、集合、并发和企业级开发基础。',
    summary: 'Java 的学习价值在于语言稳定、生态成熟，也很适合作为工程化和后端开发的入口。',
    audience: ['适合准备学后端的同学', '适合需要系统掌握面向对象的人'],
    focus: ['语言基础', '类与对象', '集合与泛型', '异常与常用 API'],
    links: [
      {
        label: 'Learn Java',
        url: 'https://dev.java/learn/',
        source: 'dev.java',
      },
    ],
  },
  {
    slug: 'go',
    title: 'Go',
    level: '后端方向',
    desc: '适合快速上手服务端开发，强调简洁语法、并发模型和工程效率。',
    summary: 'Go 很适合作为现代后端语言入门，学习成本相对可控，也方便建立工程实践意识。',
    audience: ['适合准备做后端或服务开发的同学', '适合想学习并发基础的人'],
    focus: ['语法基础', '函数与结构体', '接口与错误处理', 'goroutine 与 channel'],
    links: [
      {
        label: 'Go Learn',
        url: 'https://go.dev/learn',
        source: 'Go',
      },
      {
        label: 'A Tour of Go',
        url: 'https://go.dev/tour/',
        source: 'Go',
      },
    ],
  },
  {
    slug: 'rust',
    title: 'Rust',
    level: '系统编程',
    desc: '适合想深入系统编程、性能优化和内存安全的学习者。',
    summary: 'Rust 更强调安全和性能，学习门槛会高一些，但很适合建立严谨的编程思维。',
    audience: ['适合有一门语言基础后再学', '适合对系统编程和底层性能感兴趣的人'],
    focus: ['所有权', '借用与生命周期', '结构体与枚举', '错误处理与工程组织'],
    links: [
      {
        label: 'The Rust Programming Language',
        url: 'https://doc.rust-lang.org/book/',
        source: 'Rust',
      },
      {
        label: 'Learn Rust',
        url: 'https://www.rust-lang.org/learn/',
        source: 'Rust',
      },
    ],
  },
  {
    slug: 'vue3',
    title: 'Vue 3',
    level: '前端框架',
    desc: '适合学习现代前端组件化开发，围绕响应式、组件通信和工程实践展开。',
    summary: '如果你的目标是做前端项目，Vue 3 是很适合的主框架方向。',
    audience: ['适合已有 HTML、CSS、JavaScript 基础的人', '适合准备做前端项目开发的人'],
    focus: ['响应式基础', '模板与指令', '组件通信', '路由与项目结构'],
    links: [
      {
        label: 'Vue Guide',
        url: 'https://vuejs.org/guide/introduction.html',
        source: 'Vue',
      },
      {
        label: 'Vue Tutorial',
        url: 'https://vuejs.org/tutorial/',
        source: 'Vue',
      },
    ],
  },
]

export function getLearningTopic(slug) {
  return learningTopics.find((item) => item.slug === slug)
}
