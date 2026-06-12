export default {
  template: '\n    <q-uploader\n      ref="qRef"\n      :url="computed_url"\n    >\n      <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">\n        <slot :name="slot" v-bind="slotProps || {}" />\n      </template>\n    </q-uploader>\n  ',
  mounted() {
    setTimeout(() => this.compute_url(), 0);
  },
  updated() {
    this.compute_url();
  },
  methods: {
    compute_url() {
      this.computed_url = (this.url.startsWith("/") ? window.path_prefix : "") + this.url;
    }
  },
  props: {
    url: String
  },
  data: function() {
    return {
      computed_url: this.url
    };
  }
};
