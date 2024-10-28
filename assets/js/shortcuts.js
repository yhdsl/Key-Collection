// noinspection JSUnresolvedReference,JSIgnoredPromiseFromCall
keyboard$.subscribe(function(key) {
  if (key.mode === "global" && key.type === "ArrowLeft") {
      const prev = document.querySelector("link[rel=prev]")
      if (typeof prev !== "undefined")
          location.href = prev.href
      key.claim()
  }
  else if (key.mode === "global" && key.type === "ArrowRight") {
      const next = document.querySelector("link[rel=next]")
      if (typeof next !== "undefined")
          location.href = next.href
      key.claim()
  }
}
)
