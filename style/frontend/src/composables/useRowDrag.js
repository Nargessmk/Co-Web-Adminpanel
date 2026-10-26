import { ref } from 'vue'

/**
 * Drag and drop for the admin dialogs.
 *
 * The browser carries the row; this only remembers what is being carried and
 * what the pointer is over, so the rows can show it. The handle is the part
 * that is `draggable` and the row is the drop target, which leaves the inputs
 * inside the row free for typing.
 *
 * Every list has its own state, so a drag in one dialog never leaves a row
 * marked in another.
 */
export function useRowDrag () {
  /** Index of the row being carried, in the list it came from. */
  const dragIndex = ref(null)
  /** Row that would receive it. */
  const overIndex = ref(null)
  /** Zone (e.g. a ring) the pointer is between the rows of. */
  const overZone = ref(null)

  function startDrag (index, event) {
    dragIndex.value = index
    overZone.value = null
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move'
      // Firefox refuses to start a drag that carries no data.
      event.dataTransfer.setData('text/plain', String(index))
    }
  }

  function enterRow (index, event) {
    // Without preventDefault the browser refuses the drop.
    event.preventDefault()
    if (event.dataTransfer) event.dataTransfer.dropEffect = 'move'
    overZone.value = null
    if (dragIndex.value === null || dragIndex.value === index) return
    overIndex.value = index
  }

  function enterZone (zone) {
    overIndex.value = null
    if (dragIndex.value === null) return
    overZone.value = zone
  }

  // The pointer only really left the zone when it is no longer over anything
  // inside it, so the row it entered last keeps the highlight.
  function leaveZone (zone) {
    if (overZone.value === zone) overZone.value = null
  }

  function endDrag () {
    dragIndex.value = null
    overIndex.value = null
    overZone.value = null
  }

  /**
   * The index being carried, with the drag state cleared: the caller moves
   * the row itself, because what "moving" means depends on the list.
   */
  function takeDrag () {
    const index = dragIndex.value
    endDrag()
    return index
  }

  // The carried row is dimmed, what would receive it is outlined.
  function rowClass (index) {
    return {
      'row-dragging': dragIndex.value === index,
      'row-over': overIndex.value === index,
    }
  }

  function zoneClass (zone) {
    return { 'zone-over': overZone.value === zone }
  }

  return { dragIndex, overIndex, overZone, startDrag, enterRow, enterZone, leaveZone, endDrag, takeDrag, rowClass, zoneClass }
}

/** Moves the row at `from` to `to`, the rest of the list keeping its order. */
export function moveRowTo (rows, from, to) {
  if (!rows.value) return
  const next = rows.value.slice()
  const [moved] = next.splice(from, 1)
  next.splice(to, 0, moved)
  rows.value = next
}
