<template>
  <div>
    <section class="section">
      <div class="container">
        <div class="columns is-multiline">
          <div class="column">
            <div class="box">
              <div v-for="(message, index) in messages">
                <div v-if="message.role == 'assistant'" class="media">
                  <figure class="media-left bot-icon">
                    <p class="image is-48x48">
                      <img class="is-rounded" src="/img/segodon.png" alt="User icon"/>
                    </p>
                  </figure>
                  <div class="message" v-html="message.content"></div>
                </div>
                <span class="tag is-primary" v-if="isReceiving && message.role == 'assistant' && index==messages.length-1">回答中...</span>
                <div v-if="message.role == 'user'" class="media chat-right">
                  <div class="message">
                    {{ message.content }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="elm-input">
      <div class="container">
        <div class="columns is-multiline">
          <div class="column">
            <div class="box">
              <div class="field is-grouped">
                <div class="control is-expanded">
                  <input
                      ref="userInput"
                      v-model="userInput"
                      class="input"
                      type="text"
                      placeholder="Type your message..."
                      :class="{ 'is-focused': !isReceiving }"
                  />
                </div>
                <div class="control">
                  <button
                      class="button is-info"
                      :disabled="userInput == '' || isReceiving"
                      @click="chat"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal" :class="{ 'is-active': showModal }">
      <div class="modal-background"></div>
      <div class="modal-card">
        <section class="modal-card-body">
          {{ modalMessage }}
        </section>
        <footer class="modal-card-foot">
          <button class="button is-success" @click="showModal = false">OK</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "About",
  data() {
    return {
      messages: [],
      userInput: "",
      isToggle: false,
      isLoggedIn: false,
      showModal: false,
      modalMessage: "test",
      isReceiving: false,
    }
  },
  async mounted() {
    const apiUrl = this.$config.public.apiUrl
    try{
      const response = await fetch(`${apiUrl}/refresh`, {
        method: "POST",
        credentials: "include",
        mode: "cors",
      })
      this.init()
    }catch (e) {
      this.modalMessage = "サーバー通信でエラーが発生しました"
      this.showModal = true
    }
  },
  methods: {
    init() {
      this.messages = [
        {role: "assistant", content: "こんにちは！自由にお話しください。<b>鹿児島愛100%で</b>お返事します。"},
      ]
      this.isReceiving = false
    },
    async info() {
      try {
        const response = await fetch("http://localhost:5000/api/info", {
          method: "POST",
          body: "hoge",
          credentials: "include",
        })
        let data = await response.json()
        console.log(data)
      } catch (err) {
        console.error(err)
      }
    },
    async chat() {
      this.messages.push({role: "user", content: this.userInput})
      this.messages.push({role: "assistant", content: ""})
      const userMessage = this.userInput
      this.userInput = ""

      this.$nextTick(function () {
        window.scrollTo(0, document.body.scrollHeight)
      })
      this.isReceiving = true
      try {
        const apiUrl = this.$config.public.apiUrl
        const response = await fetch(`${apiUrl}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "text/plain",
          },
          body: userMessage,
          credentials: "include",
          mode: "cors",
        })
        if (!response.ok) {
          console.log(response.status)
          this.modalMessage = await response.text()
          this.showModal = true
          this.init()
          return
        }
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        while (true) {
          const {done, value} = await reader.read()
          if (done) {
            break
          }
          const text = decoder.decode(value, {stream: true})
          this.messages[this.messages.length - 1].content += text.replace("\n", "<br/>")
        }
        this.$nextTick(function () {
          window.scrollTo(0, document.body.scrollHeight)
        })
      } catch (err) {
        console.error(err)
        this.modalMessage = "サーバー通信でエラーが発生しました"
        this.showModal = true
      } finally {
        this.isReceiving = false
        this.$refs.userInput.focus();
      }
    },
    async send() {
      this.messages.push({role: "user", content: this.userInput})
      this.messages.push({role: "assistant", content: ""})
      const userMessage = this.userInput
      this.userInput = ""

      this.$nextTick(function () {
        window.scrollTo(0, document.body.scrollHeight)
      })

      const response = await fetch("/api/mock", {
        method: "POST",
        headers: {
          "Content-Type": "text/plain",
        },
        body: userMessage,
      })
      if (!response.ok) throw new Error(await response.text())
      const reader = response.body.getReader()
      // another option:
      // const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();

      const decoder = new TextDecoder()
      while (true) {
        const {done, value} = await reader.read()
        if (done) {
          break
        }
        const text = decoder.decode(value, {stream: true})
        console.log(text)
        this.messages[this.messages.length - 1].content += text
      }
    },
    // login() {
    //   this.isLoggedIn = true
    // },
    // logout() {
    //   this.isLoggedIn = false
    // },
  },
}
</script>

<style lang="scss">
.message {
  max-width: 80%;
  padding: 10px;
  word-wrap: break-word;
}

.bot-icon {
  margin-left: 5px !important;
  margin-right: 5px !important;
}

.chat-right {
  justify-content: flex-end;
}

.media{
  margin-bottom: 1em;
}

.elm-input {
  position: fixed;
  bottom: 0;
  width: 100%;
}

body {
  padding-bottom: 80px;
}

.title2 {
  color: #fa7c91;
}
</style>
