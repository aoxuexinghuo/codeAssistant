export const learningTopics = [
  {
    slug: 'c-language',
    initial: 'C',
    title: 'C 语言',
    level: '基础语言',
    desc: '理解内存、指针、过程式编程和系统级思维。',
    summary: 'C 语言适合打牢计算机基础，尤其适合理解内存和程序执行方式。',
    audience: ['编程初学者', '准备学习数据结构、操作系统或嵌入式的人'],
    focus: ['基础语法', '指针与数组', '函数与文件组织', '内存与输入输出'],
    links: [
      {
        label: 'C language reference',
        url: 'https://en.cppreference.com/w/c/language.html',
        source: 'cppreference',
      },
      {
        label: 'C standard library',
        url: 'https://en.cppreference.com/w/c.html',
        source: 'cppreference',
      },
    ],
  },
  {
    slug: 'java',
    initial: 'J',
    title: 'Java',
    level: '工程语言',
    desc: '系统学习面向对象、集合、异常和后端开发基础。',
    summary: 'Java 生态成熟，适合作为后端工程化和面向对象编程的入口。',
    audience: ['准备学习后端开发的人', '想系统掌握面向对象的人'],
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
    slug: 'python',
    initial: 'Py',
    title: 'Python',
    level: '入门友好',
    desc: '适合快速理解编程基础、脚本处理和后端入门。',
    summary: 'Python 语法简洁，适合作为编程入门和数据处理、Web 开发的起点。',
    audience: ['编程初学者', '想快速做脚本、自动化或后端原型的人'],
    focus: ['基础语法', '函数与模块', '列表和字典', '异常处理'],
    links: [
      {
        label: 'Python Tutorial',
        url: 'https://docs.python.org/3/tutorial/',
        source: 'Python',
      },
      {
        label: 'Python Standard Library',
        url: 'https://docs.python.org/3/library/',
        source: 'Python',
      },
    ],
  },
  {
    slug: 'go',
    initial: 'Go',
    title: 'Go',
    level: '后端方向',
    desc: '适合快速上手服务端开发，重点是并发和工程效率。',
    summary: 'Go 学习成本相对可控，很适合作为现代后端语言入口。',
    audience: ['准备做后端或服务开发的人', '想学习并发基础的人'],
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
    initial: 'Rs',
    title: 'Rust',
    level: '系统编程',
    desc: '围绕所有权、借用、生命周期和内存安全建立严谨思维。',
    summary: 'Rust 门槛更高，但非常适合建立安全、严谨的编程习惯。',
    audience: ['已有一门语言基础的人', '对系统编程和性能优化感兴趣的人'],
    focus: ['所有权', '借用与生命周期', '结构体与枚举', '错误处理与项目组织'],
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
    initial: 'V3',
    title: 'Vue 3',
    level: '前端框架',
    desc: '学习组件化、响应式、路由和前端项目组织。',
    summary: 'Vue 3 适合进入现代前端项目开发，重点是响应式和组件化思维。',
    audience: ['已有 HTML、CSS、JavaScript 基础的人', '准备做前端项目开发的人'],
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
