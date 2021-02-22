import './Conversations.css'

import React, { Component } from "react"
import Cookies from 'universal-cookie'
import { Table, UncontrolledTooltip } from "reactstrap"
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'


class Conversations extends Component {
    constructor(props) {
        super(props)
        const cookies = new Cookies()

        this.state = {
            cookies,
            favorites: cookies.get("favorites") || {}
        }
    }

    toggleFavorite = (item, value) => {
        const { favorites } = this.state
        favorites[item.id] = value
        this.setState({ favorites })
        this.state.cookies.set("favorites", favorites)
    }

    handleDelete = item => {
        this.toggleFavorite(item, false)
        this.props.onDelete(item)
    }

    render() {
        return <div>
            <h4>
                <span className="mr-3">Conversations</span>
                <span
                    onClick={() => this.props.onRefresh()}
                    id="RefreshButton"
                    className={"btn-icon mr-3"}
                >
                    <FontAwesomeIcon icon="sync" size="sm" />
                </span>
            </h4>
            {this.props.items.length > 0 ? (
                <Table className="conversations-table mt-5">
                    <thead>
                        <tr>
                            <th scope="col id" style={{ width: '10%' }}>Id</th>
                            <th scope="col text" style={{ width: '50%' }}>Text</th>
                            <th scope="col lastMutation" style={{ width: '30%' }}>Last Mutation</th>
                            <th scope="col actions" style={{ width: '10%' }}></th>
                        </tr>
                    </thead>
                    <tbody id="conversationsContainer">
                        {this.renderItems()}
                    </tbody>
                </Table>
            ) : <h5 className="mt-5 pb-3 text-center">There are no conversations saved yet</h5>}
        </div>
    }

    renderItems = () => {
        return this.props.items.map(item => {
            if (item.hidden) return

            const authors = Object.keys(item.lastMutation.origin)
            const originArr = []
            authors.forEach(author => {
                originArr.push(`"${author}": ${item.lastMutation.origin[author]}`)
            })

            let actionStr = "performed a mutation with unknown type at"
            if (item.lastMutation.data.type === "insert") {
                actionStr = `inserted "${item.lastMutation.data.text}" to`
            } else if (item.lastMutation.data.type === "delete") {
                actionStr = `deleted ${item.lastMutation.data.length} characters from`
            }

            const lastMutationPretty = `${item.lastMutation.author} ${actionStr} index ${item.lastMutation.data.index}\norigin = {${originArr.join(", ")}}`
            return <tr>
                <th scope="row" class="id">{item.id}</th>
                <td className="text">{item.text}</td>
                <td className="lastMutation"><pre>{lastMutationPretty}</pre></td>
                <td className="actions text-nowrap">
                    <span
                        onClick={() => this.props.onSelect(item)}
                        id={`ViewButton-${item.id}`}
                        className={"btn-icon mr-3"}
                    >
                        <FontAwesomeIcon icon="comments" size="lg" />
                        <UncontrolledTooltip
                            placement="top" target={`ViewButton-${item.id}`}
                            trigger="hover">View in Real-Time</UncontrolledTooltip>
                    </span>
                    <span
                        onClick={() => this.toggleFavorite(item, !(item in this.state.favorites))}
                        id={`FavoriteButton-${item.id}`}
                        className={`btn-icon mr-3 `}
                    >
                        <FontAwesomeIcon icon="star" size="lg"
                            className={this.state.favorites[item.id] ? "starred" : ""}/>
                            <UncontrolledTooltip
                                placement="top" target={`FavoriteButton-${item.id}`}
                                trigger="hover">Toggle Favorite</UncontrolledTooltip>
                    </span>
                    <span
                        onClick={() => this.handleDelete(item)}
                        id={`DeleteButton-${item.id}`}
                        className="btn-icon"
                    >
                        <FontAwesomeIcon icon="trash" size="lg" />
                        <UncontrolledTooltip
                            placement="top" target={`DeleteButton-${item.id}`}
                            trigger="hover">Delete</UncontrolledTooltip>
                    </span>
                </td>
            </tr>
        })
    }
}

export default Conversations