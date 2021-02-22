import React, { Component } from "react";
import {
	Button,
	Modal,
	ModalHeader,
	ModalBody,
	ModalFooter,
} from "reactstrap";

export default class ConversationModal extends Component {
	constructor(props) {
		super(props);
		this.state = {
			activeItem: this.props.activeItem
		};
	}
	
	render() {
		const { activeItem, onToggle } = this.props;
		if (!activeItem) return

		return (
			<Modal isOpen={true} toggle={onToggle}>
				<ModalHeader toggle={onToggle}>
					<h5>Conversation Id {this.props.activeItem.id}</h5>
				</ModalHeader>
				<ModalBody>
					<pre>{this.props.activeItem.text}</pre>
				</ModalBody>
				<ModalFooter>
					<Button color="success" onClick={onToggle}>
						Close
              		</Button>
				</ModalFooter>
			</Modal>
		);
	}
}