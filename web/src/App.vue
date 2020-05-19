<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  created() {
    this.$store.dispatch('resource/loadAttributeType')
    this.$store.dispatch('resource/loadResourceDefined')
  }
}
</script>
