import './App.css'

import React, { Component } from "react"

import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'

import axios from "axios"
import { w3cwebsocket as WebSocket } from "websocket"

import Conversations from "./components/Conversations"
import ConversationModal from "./components/ConversationModal"

// Initiate FontAwesome library with solid svg icons
library.add(fas)

// Set up to use csrf tokens by default when making api calls
axios.defaults.xsrfCookieName = "csrftoke"
axios.defaults.xsrfHeaderName = "X-CSRFToke"
axios.defaults.withCredentials = true

// Configure WebSocket client to listen to localhost
const webSocket = new WebSocket('ws://localhost:8000')


class App extends Component {
	constructor(props) {
		super(props)

        this.state = {
			conversationDict: {},
			redisClient: null
        }
	}

	componentWillMount = () => {
		this.initWebSocketClient()
	}

	componentDidMount = () => {
		this.retrieveConversations()
	}

    retrieveConversations = () => {
        axios.get("/api/conversations/")
            .then(res => {
				const conversationDict = {}
				res.data.conversations.reduce(
					(acc, item) => { acc[item.id] = item }, conversationDict)
				this.setState({ conversationDict })
			})
            .catch(err => console.log(err))
	}
	
	initWebSocketClient = () => {
		webSocket.onopen = () => {
			console.log('WebSocket Client Connected')
		}

		webSocket.onmessage = (message) => {
			if (this.state.isListening) {
				console.log('WebSocket Client received message: ', message)
				const jsonData = JSON.parse(message.data)
				
				const activeItem = this.state.activeItem || null
				console.log(activeItem, 
					jsonData.eventType === "mutation",
					activeItem.id === jsonData.conversationId,
					activeItem.lastMutation.id, jsonData.mutationId)
				if (activeItem && 
					jsonData.eventType === "mutation" &&
					activeItem.id === jsonData.conversationId &&
					activeItem.lastMutation.id < jsonData.mutationId) {
					this.state.activeItem.text = jsonData.text
					this.setState({ activeItem: this.state.activeItem })
				}
			}
		}

		webSocket.onclose = (message) => {
			console.log('WebSocket Client Disconnected')
		}
	}

	handleSelect = activeItem => {
		this.setState({ activeItem, isListening: true })
		webSocket.send(`sub:cnv:${activeItem.id}:mutation_event`)
	}
	
	handleDeselect = () => {
		webSocket.send(`unsub:cnv:${this.state.activeItem.id}:mutation_event`)
		this.setState({ activeItem: null, isListening: false })
	}

    handleDelete = item => {
        item.hidden = true
        
        axios.delete(`/api/conversations/`, { data: { conversationId: item.id } })
            .then(() => {
				const conversationDict = this.state.conversationDict
				delete conversationDict[item.id]
				this.setState({ conversationDict })
			})
            .catch(err => console.log(err))
	}

	render() {
		const { conversationDict, activeItem } = this.state
		const conversationList = Object.values(conversationDict)
		return (
			<main className="content">
				<div className="row">
					<div className="col-md-6 col-sm-10 mx-auto p-0">
						<h2 className="my-4">Operational Transformation</h2>
						<div className="card p-3">
							<Conversations
								onSelect={item => this.handleSelect(item)}
								onDelete={item => this.handleDelete(item)}
								onRefresh={() => this.retrieveConversations()}
								items={conversationList}
								activeItem={activeItem}
							/>
						</div>
					</div>
				</div>
				{activeItem ? (
					<ConversationModal
						activeItem={activeItem}
						onToggle={() => this.handleDeselect()}
					/>
				) : null}
			</main>
		)
	}
}

export default App