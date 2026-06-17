let authRouter = null

export const setAuthRouter = (router) => {
  authRouter = router
}

export const redirectToLogin = async () => {
  if (!authRouter) {
    window.location.assign('/login')
    return
  }

  const currentRoute = authRouter.currentRoute.value

  if (currentRoute.path === '/login') {
    return
  }

  await authRouter.replace({
    path: '/login',
    query: currentRoute.fullPath ? { redirect: currentRoute.fullPath } : {}
  })
}
