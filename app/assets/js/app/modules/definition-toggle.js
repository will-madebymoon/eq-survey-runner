import { forEach } from 'lodash'
import domready from './domready'

export const classDefinition = 'js-definition'
export const classTrigger = 'js-definition-trigger'
export const classBody = 'js-definition-body'
export const classLabel = 'js-definition-label'
export const classExpandedState = 'is-expanded'

export const attrShowLbl = 'data-show-label'
export const attrHideLbl = 'data-hide-label'
export const attrAriaExpanaded = 'aria-expanded'
export const attrAriaHidden = 'aria-hidden'
export const attrTabIndex = 'tabindex'

export default function() {
  return definitionToggle()
}

export function definitionToggle() {
  const nodeList = document.getElementsByClassName(classDefinition)
  forEach(nodeList, applyDefinitionToggle)
  return nodeList
}

export function applyDefinitionToggle(elDefinition) {
  const elTrigger = elDefinition.getElementsByClassName(classTrigger)[0]
  const elBody = elDefinition.getElementsByClassName(classBody)[0]
  const elLabel = elDefinition.getElementsByClassName(classLabel)[0]
  let toggled = false

  elTrigger.addEventListener('click', e => {
    e.preventDefault()
    toggled = toggle(toggled, elDefinition, elTrigger, elBody, elLabel)
    return false
  })

  return { elDefinition, elTrigger, elBody }
}

export function open(elDefinition, elBody, elLabel, elTrigger) {
  elDefinition.classList.add(classExpandedState)
  elLabel.innerHTML = elDefinition.getAttribute(attrHideLbl)
  elTrigger.setAttribute(attrAriaExpanaded, true)
  elBody.setAttribute(attrAriaHidden, false)
}

export function close(elDefinition, elBody, elLabel, elTrigger) {
  elDefinition.classList.remove(classExpandedState)
  elLabel.innerHTML = elDefinition.getAttribute(attrShowLbl)
  elTrigger.setAttribute(attrAriaExpanaded, false)
  elBody.setAttribute(attrAriaHidden, true)
}

export function toggle(toggled, elDefinition, elTrigger, elBody, elLabel) {
  !toggled
    ? open(elDefinition, elBody, elLabel, elTrigger)
    : close(elDefinition, elBody, elLabel, elTrigger)
  return !toggled
}

domready(definitionToggle)
