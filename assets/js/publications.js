(function () {
  var buttons = document.querySelectorAll(".filters button");
  var search = document.getElementById("pub-search");
  var groups = document.querySelectorAll(".year-group");
  var empty = document.getElementById("pub-empty");
  var filter = "all";

  function update() {
    var q = search.value.trim().toLowerCase();
    var shown = 0;
    groups.forEach(function (g) {
      var visibleInGroup = 0;
      g.querySelectorAll("li").forEach(function (li) {
        var ok = (filter === "all" || li.dataset.type === filter) &&
                 (!q || li.dataset.search.indexOf(q) !== -1);
        li.hidden = !ok;
        if (ok) visibleInGroup++;
      });
      g.hidden = visibleInGroup === 0;
      shown += visibleInGroup;
    });
    empty.hidden = shown !== 0;
  }

  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      filter = b.dataset.filter;
      buttons.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      update();
    });
  });
  search.addEventListener("input", update);
})();
