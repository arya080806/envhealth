import { load_widget, load_css } from "widget";
import { cleanObject } from "../../static/utils/json.js";
export default {
  template: "<div></div>",
  async mounted() {
    var _a, _b;
    const emit_to_py = this.$emit;
    this.model = {
      attributes: { ...this.traits },
      callbacks: {},
      get: function(key) {
        return cleanObject(this.attributes[key]);
      },
      set: function(key, value) {
        this.attributes[key] = value;
        this.emit("change:" + key, value);
      },
      save_changes: function() {
        if (this.callbacks.change && Array.isArray(this.callbacks.change)) {
          this.callbacks.change.forEach((cb) => cb());
        }
        emit_to_py("update:traits", { ...this.attributes });
      },
      on: function(event, callback) {
        if (!this.callbacks[event]) this.callbacks[event] = [];
        this.callbacks[event].push(callback);
      },
      off: function(event, callback) {
        var _a2;
        if (!event) this.callbacks = {};
        else if (!callback) this.callbacks[event] = [];
        else (_a2 = this.callbacks[event]) == null ? void 0 : _a2.delete(callback);
      },
      emit: function(event, value) {
        var _a2;
        (_a2 = this.callbacks[event]) == null ? void 0 : _a2.forEach((cb) => cb(value));
      },
      send: function(content, callbacks, buffers) {
        console.warn("anywidget.send() is not yet implemented in NiceGUI", content);
      }
    };
    const mod = await load_widget(this.esm_content, this.traits._anywidget_id);
    this.cleanup_widget = await ((_a = mod.initialize) == null ? void 0 : _a.call(mod, { model: this.model }));
    this.cleanup_view = await ((_b = mod.render) == null ? void 0 : _b.call(mod, { model: this.model, el: this.$el }));
    load_css(this.css_content, this.traits._anywidget_id);
  },
  methods: {
    update_trait(trait, value) {
      this.model.set(trait, value);
    }
  },
  props: {
    traits: Object,
    esm_content: String,
    css_content: String
  }
};
