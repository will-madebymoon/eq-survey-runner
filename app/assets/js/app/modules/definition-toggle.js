import { forEach } from 'lodash'
import domready from './domready'

export const classDefinition = 'js-definition'
export const classTrigger = 'js-definition-trigger'

export const dialogCall = 'data-dialog-call'
export const dialogResponse = 'data-dialog-response'

export default function() {
  return definitionToggle()
}

export function definitionToggle() {
  const nodeList = document.getElementsByClassName(classTrigger)
  forEach(nodeList, applyDefinitionToggle)
  return nodeList
}

export function applyDefinitionToggle(elDefinition) {
  let toggled = false

  elDefinition.addEventListener('click', e => {
    e.preventDefault()
    return false
  })

  return { elDefinition }
}

domready(definitionToggle)
