export default {
  template: '<video :controls="controls" :autoplay="autoplay" :muted="muted" :src="computed_src" />',
  props: {
    controls: Boolean,
    autoplay: Boolean,
    muted: Boolean,
    src: String
  },
  data: function() {
    return {
      computed_src: void 0
    };
  },
  mounted() {
    setTimeout(() => this.compute_src(), 0);
  },
  updated() {
    this.compute_src();
  },
  methods: {
    compute_src() {
      this.computed_src = (this.src.startsWith("/") ? window.path_prefix : "") + this.src;
    },
    seek(seconds) {
      this.$el.currentTime = seconds;
    },
    play() {
      this.$el.play();
    },
    pause() {
      this.$el.pause();
    }
  }
};
