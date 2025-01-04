# app/routes/initiative.py    
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app import db
from app.models.initiative import Initiative, InitiativeParticipant
from app.utils.activity import create_activity

initiative_bp = Blueprint('initiative', __name__)

# Updated create_initiative function
@initiative_bp.route('', methods=['POST'])
@jwt_required()
def create_initiative():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'description', 'location', 'event_date', 'duration_hours']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Parse the date string to datetime object
        # First, try ISO format
        try:
            event_date = datetime.fromisoformat(data['event_date'].replace('Z', '+00:00'))
        except ValueError:
            # If ISO format fails, try parsing common datetime format
            event_date = datetime.strptime(data['event_date'], '%Y-%m-%dT%H:%M')
            event_date = event_date.replace(tzinfo=timezone.utc)
        
        # Get current time
        current_time = datetime.now(timezone.utc)
        
        # Compare only the date components if you want to allow same-day events
        if event_date.date() < current_time.date():
            return jsonify({'error': 'Event date cannot be in the past'}), 400
            
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    
    # Set default values for optional fields
    max_participants = data.get('max_participants', 50)  # Default to 50 if not specified
    requirements = data.get('requirements', '')
    contact_info = data.get('contact_info', '')
    
    initiative = Initiative(
        title=data['title'],
        description=data['description'],
        location=data['location'],
        event_date=event_date,
        duration_hours=float(data['duration_hours']),
        max_participants=max_participants,
        requirements=requirements,
        contact_info=contact_info,
        created_by=current_user_id,
        status='upcoming'  # Explicitly set initial status
    )
    
    try:
        db.session.add(initiative)
        db.session.commit()
        
        # Create activity feed entry
        create_activity(
            current_user_id,
            'initiative_created',
            f"Created new initiative: {initiative.title}",
            initiative.id
        )
        
        return jsonify({
            'message': 'Initiative created successfully',
            'initiative': initiative.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
@initiative_bp.route('', methods=['GET'])
def get_initiatives():
    # Get query parameters
    status = request.args.get('status', 'upcoming')
    location = request.args.get('location')
    
    # Base query
    query = Initiative.query
    
    # Filter by status
    if status != 'all':
        query = query.filter_by(status=status)
    
    # Filter by location if provided
    if location:
        query = query.filter(Initiative.location.ilike(f'%{location}%'))
    
    # Get current time as timezone-aware datetime
    current_time = datetime.now(timezone.utc)
    
    # Update status based on event date
    initiatives = query.all()
    for initiative in initiatives:
        # Make sure initiative.event_date is timezone-aware
        if not initiative.event_date.tzinfo:
            initiative_date = initiative.event_date.replace(tzinfo=timezone.utc)
        else:
            initiative_date = initiative.event_date
            
        if initiative_date < current_time and initiative.status == 'upcoming':
            initiative.status = 'completed'
    
    db.session.commit()
    
    # Order by date
    initiatives = sorted(initiatives, key=lambda x: x.event_date)
    
    return jsonify({
        'initiatives': [init.to_dict() for init in initiatives]
    }), 200

@initiative_bp.route('/<int:initiative_id>', methods=['GET'])
def get_initiative(initiative_id):
    initiative = Initiative.query.get_or_404(initiative_id)
    return jsonify({'initiative': initiative.to_dict()}), 200

@initiative_bp.route('/<int:initiative_id>/join', methods=['POST'])
@jwt_required()
def join_initiative(initiative_id):
    current_user_id = int(get_jwt_identity())
    
    try:
        initiative = Initiative.query.get_or_404(initiative_id)
        
        # Check if initiative is upcoming
        if initiative.status != 'upcoming':
            return jsonify({'error': 'Can only join upcoming initiatives'}), 400
        
        # Check if already joined
        existing_participant = InitiativeParticipant.query.filter_by(
            initiative_id=initiative_id,
            user_id=current_user_id
        ).first()
        
        if existing_participant and existing_participant.status == 'joined':
            return jsonify({'error': 'Already joined this initiative'}), 400
        
        # Get current participants count
        current_participants = InitiativeParticipant.query.filter_by(
            initiative_id=initiative_id,
            status='joined'
        ).count()
        
        # Check max participants limit
        if initiative.max_participants and current_participants >= initiative.max_participants:
            return jsonify({'error': 'Initiative has reached maximum participants'}), 400
        
        # Create or update participant
        if existing_participant:
            existing_participant.status = 'joined'
            participant = existing_participant
        else:
            participant = InitiativeParticipant(
                initiative_id=initiative_id,
                user_id=current_user_id,
                status='joined'
            )
            db.session.add(participant)
        
        db.session.commit()
        
        # Create activity feed entry
        create_activity(
            current_user_id,
            'initiative_joined',
            f"Joined initiative: {initiative.title}",
            initiative.id
        )
        
        # Return updated initiative data
        initiative_data = initiative.to_dict()
        initiative_data['participants'] = [
            p.user_id for p in InitiativeParticipant.query.filter_by(
                initiative_id=initiative_id,
                status='joined'
            ).all()
        ]
        
        return jsonify({
            'message': 'Successfully joined initiative',
            'initiative': initiative_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error joining initiative: {str(e)}'}), 500

@initiative_bp.route('/<int:initiative_id>/participants', methods=['GET'])
def get_participants(initiative_id):
    initiative = Initiative.query.get_or_404(initiative_id)
    
    participants = InitiativeParticipant.query.filter_by(
        initiative_id=initiative_id,
        status='joined'
    ).all()
    
    return jsonify({
        'participants': [participant.to_dict() for participant in participants]
    }), 200

@initiative_bp.route('/<int:initiative_id>', methods=['PUT'])
@jwt_required()
def update_initiative(initiative_id):
    current_user_id = get_jwt_identity()
    
    initiative = Initiative.query.get_or_404(initiative_id)
    
    # Check if user is the creator
    if initiative.created_by != current_user_id:
        return jsonify({'error': 'Unauthorized to update this initiative'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data:
        initiative.title = data['title']
    if 'description' in data:
        initiative.description = data['description']
    if 'requirements' in data:
        initiative.requirements = data['requirements']
    if 'contact_info' in data:
        initiative.contact_info = data['contact_info']
    if 'status' in data:
        initiative.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Initiative updated successfully',
        'initiative': initiative.to_dict()
    }), 200