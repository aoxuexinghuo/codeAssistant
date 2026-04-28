import { createRouter, createWebHistory } from 'vue-router'
import AppShell from '../components/layout/AppShell.vue'
import AuthView from '../views/AuthView.vue'
import AssistantView from '../views/AssistantView.vue'
import HomeView from '../views/HomeView.vue'
import LearningDetailView from '../views/LearningDetailView.vue'
import LearningCenterView from '../views/LearningCenterView.vue'
import MistakesView from '../views/MistakesView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
  {
    path: '/',
    redirect: '/auth/login',
  },
  {
    path: '/auth/:mode(login|register)',
    name: 'auth',
    component: AuthView,
  },
  {
    path: '/',
    component: AppShell,
    children: [
      {
        path: 'home',
        name: 'home',
        component: HomeView,
      },
      {
        path: 'learning',
        name: 'learning',
        component: LearningCenterView,
      },
      {
        path: 'learning/:slug',
        name: 'learning-detail',
        component: LearningDetailView,
      },
      {
        path: 'mistakes',
        name: 'mistakes',
        component: MistakesView,
      },
      {
        path: 'profile',
        name: 'profile',
        component: ProfileView,
      },
      {
        path: 'assistant',
        name: 'assistant',
        component: AssistantView,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
