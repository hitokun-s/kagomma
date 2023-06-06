<template>
  <div>
    <nav class="navbar" role="navigation" aria-label="main navigation">
      <div class="container is-fluid">
        <div class="navbar-brand">
          <NuxtLink class="navbar-item" to="/">
            <!--<img class="image" src="https://bulma.io/images/bulma-logo.png" alt="" width="96px">-->
            <h1 class="title">KAGOMM<span class="title2">A.I</span></h1>
          </NuxtLink>
          <a
              class="navbar-burger"
              role="button"
              aria-label="menu"
              aria-expanded="false"
              data-target="menu"
              @click="isToggle = !isToggle"
          >
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </a>
        </div>
        <div id="menu" class="navbar-menu" :class="{ 'is-active': isToggle }">
          <div class="navbar-start">
            <!--            <a class="navbar-item" href="https://twitter.com/ginyu_pro">creator</a>-->
            <!--            <a class="navbar-item" href="https://docs.google.com/forms/d/e/1FAIpQLSeGm6pd62UbE36bVkxnRR5CMtphW_gd-fJhgHy6dPI6Npxdyg/viewform?usp=sf_link">contact</a>-->
            <!--            <a class="navbar-item" href="#">about</a>-->
          </div>
          <div class="navbar-end">
            <a class="navbar-item" target="_blank" href="https://docs.google.com/forms/d/e/1FAIpQLSeGm6pd62UbE36bVkxnRR5CMtphW_gd-fJhgHy6dPI6Npxdyg/viewform?usp=sf_link">contact</a>
            <NuxtLink class="navbar-item" to="/about">about</NuxtLink>
            <!--            <div v-if="isLoggedIn" class="navbar-item">-->
            <!--              <span class="icon">-->
            <!--                <font-awesome-icon icon="user" size="2x" :style="{ color: 'grey' }" />-->
            <!--              </span>-->
            <!--            </div>-->
            <!--            <div class="navbar-item">-->
            <!--              <button v-if="!isLoggedIn" class="button" @click="login">login</button>-->
            <!--              <button v-if="isLoggedIn" class="button" @click="logout">logout</button>-->
            <!--            </div>-->
          </div>
        </div>
      </div>
    </nav>
    <slot />
  </div>
</template>

<script>
export default {
  data() {
    return {
      isToggle: false,
    }
  }
}
</script>

<style>
.title2 {
  color: #fa7c91;
}
</style>
