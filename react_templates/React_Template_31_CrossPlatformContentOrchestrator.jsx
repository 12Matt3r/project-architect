/**
 * Template #31: Cross-Platform Content Orchestrator
 * React frontend for multi-format content generation
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Input,
  Textarea,
  Image,
  Card,
  CardHeader,
  CardBody,
  Grid,
  GridItem,
  Badge,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  useToast,
  FormControl,
  FormLabel,
  Select,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Code,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Wrap,
  WrapItem,
  Tag,
  TagLabel,
  TagCloseButton,
  Icon,
  Flex,
  Spacer
} from '@chakra-ui/react';
import {
  FiUpload,
  FiTwitter,
  FiLinkedin,
  FiMic,
  FiImage,
  FiEye,
  FiShare2,
  FiRefreshCw,
  FiDownload,
  FiTrendingUp,
  FiUsers,
  FiTarget,
  FiZap
} from 'react-icons/fi';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

const CrossPlatformContentOrchestrator = () => {
  const [topic, setTopic] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [campaignName, setCampaignName] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [brandVoice, setBrandVoice] = useState('professional');
  const [customInstructions, setCustomInstructions] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [campaign, setCampaign] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const { isOpen: isImageModalOpen, onOpen: onImageModalOpen, onClose: onImageModalClose } = useDisclosure();
  const toast = useToast();

  // Handle image selection
  const handleImageSelect = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  // Handle campaign generation
  const generateCampaign = useCallback(async () => {
    if (!topic.trim()) {
      toast({
        title: 'Topic Required',
        description: 'Please enter a topic for content generation.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsGenerating(true);
    try {
      const formData = new FormData();
      formData.append('topic', topic);
      if (selectedImage) {
        formData.append('image', selectedImage);
      }
      if (campaignName) formData.append('campaign_name', campaignName);
      if (targetAudience) formData.append('target_audience', targetAudience);
      formData.append('brand_voice', brandVoice);
      if (customInstructions) formData.append('custom_instructions', customInstructions);

      const response = await fetch(`${API_BASE_URL}/api/v1/generate-campaign`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setCampaign(result);
      
      // Fetch analytics
      fetchAnalytics(result.campaign_id);

      toast({
        title: 'Campaign Generated!',
        description: 'Your cross-platform content campaign is ready.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      console.error('Error generating campaign:', error);
      toast({
        title: 'Generation Failed',
        description: 'Failed to generate content campaign. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsGenerating(false);
    }
  }, [topic, selectedImage, campaignName, targetAudience, brandVoice, customInstructions]);

  // Fetch campaign analytics
  const fetchAnalytics = useCallback(async (campaignId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/analytics/${campaignId}`);
      if (response.ok) {
        const analyticsData = await response.json();
        setAnalytics(analyticsData);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  }, []);

  // Content piece component
  const ContentPiece = ({ piece, platform, icon: PlatformIcon }) => (
    <Card shadow="md" borderWidth="1px" _hover={{ shadow: 'lg' }} transition="all 0.2s">
      <CardHeader>
        <HStack spacing={3}>
          <Icon as={PlatformIcon} color={`${platform}.500`} boxSize={6} />
          <Heading size="md" textTransform="capitalize">{platform}</Heading>
          <Badge colorScheme={piece.consistency_score > 0.8 ? 'green' : piece.consistency_score > 0.6 ? 'yellow' : 'red'}>
            {Math.round(piece.consistency_score * 100)}% Match
          </Badge>
        </HStack>
        <Text fontSize="sm" color="gray.600" mt={2}>
          {piece.title}
        </Text>
      </CardHeader>
      <CardBody>
        <VStack align="stretch" spacing={4}>
          <Box 
            p={4} 
            bg="gray.50" 
            borderRadius="md" 
            borderLeft="4px" 
            borderColor={`${platform}.500`}
            maxH="400px"
            overflowY="auto"
          >
            <Text whiteSpace="pre-wrap" fontSize="sm" lineHeight="relaxed">
              {piece.content}
            </Text>
          </Box>
          
          <HStack justify="space-between" align="center">
            <Text fontSize="xs" color="gray.500">
              {piece.metadata?.word_count || piece.content.length} characters
            </Text>
            <HStack spacing={2}>
              <Button 
                size="sm" 
                variant="outline" 
                leftIcon={<FiShare2 />}
                onClick={() => {
                  navigator.clipboard.writeText(piece.content);
                  toast({
                    title: 'Copied to clipboard',
                    status: 'success',
                    duration: 2000,
                  });
                }}
              >
                Copy
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                leftIcon={<FiEye />}
                onClick={() => {
                  // Show full content in modal
                }}
              >
                Preview
              </Button>
            </HStack>
          </HStack>

          {piece.metadata && (
            <Box>
              <Text fontSize="xs" color="gray.600" mb={2}>Key Metrics:</Text>
              <Wrap>
                {Object.entries(piece.metadata).map(([key, value]) => (
                  <WrapItem key={key}>
                    <Tag size="sm" variant="outline">
                      <TagLabel>{key.replace('_', ' ')}: {value}</TagLabel>
                    </Tag>
                  </WrapItem>
                ))}
              </Wrap>
            </Box>
          )}
        </VStack>
      </CardBody>
    </Card>
  );

  // Platform tabs component
  const PlatformTabs = () => (
    <Tabs index={activeTab} onChange={setActiveTab} colorScheme="blue">
      <TabList>
        <Tab>
          <HStack spacing={2}>
            <Icon as={FiTwitter} />
            <Text>Twitter</Text>
          </HStack>
        </Tab>
        <Tab>
          <HStack spacing={2}>
            <Icon as={FiLinkedin} />
            <Text>LinkedIn</Text>
          </HStack>
        </Tab>
        <Tab>
          <HStack spacing={2}>
            <Icon as={FiMic} />
            <Text>Podcast</Text>
          </HStack>
        </Tab>
      </TabList>

      <TabPanels>
        {campaign?.content_pieces?.map((piece, index) => (
          <TabPanel key={piece.platform} p={0} pt={4}>
            <ContentPiece 
              piece={piece} 
              platform={piece.platform}
              icon={piece.platform === 'twitter' ? FiTwitter : 
                   piece.platform === 'linkedin' ? FiLinkedin : FiMic}
            />
          </TabPanel>
        ))}
      </TabPanels>
    </Tabs>
  );

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="2xl" mb={4}>
            Cross-Platform Content Orchestrator
          </Heading>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Generate consistent, engaging content across Twitter, LinkedIn, and Podcast formats 
            with AI-powered visual analysis and brand voice optimization.
          </Text>
        </Box>

        {/* Input Section */}
        <Card>
          <CardHeader>
            <Heading size="lg">Campaign Configuration</Heading>
            <Text color="gray.600">Configure your content generation parameters</Text>
          </CardHeader>
          <CardBody>
            <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={6}>
              <GridItem>
                <VStack spacing={6} align="stretch">
                  {/* Topic Input */}
                  <FormControl isRequired>
                    <FormLabel>Content Topic</FormLabel>
                    <Input
                      placeholder="Enter your main topic (e.g., 'Sustainable Business Practices')"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      size="lg"
                    />
                  </FormControl>

                  {/* Campaign Name */}
                  <FormControl>
                    <FormLabel>Campaign Name (Optional)</FormLabel>
                    <Input
                      placeholder="Give your campaign a name"
                      value={campaignName}
                      onChange={(e) => setCampaignName(e.target.value)}
                    />
                  </FormControl>

                  {/* Target Audience */}
                  <FormControl>
                    <FormLabel>Target Audience</FormLabel>
                    <Input
                      placeholder="Describe your target audience"
                      value={targetAudience}
                      onChange={(e) => setTargetAudience(e.target.value)}
                    />
                  </FormControl>

                  {/* Brand Voice */}
                  <FormControl>
                    <FormLabel>Brand Voice</FormLabel>
                    <Select value={brandVoice} onChange={(e) => setBrandVoice(e.target.value)}>
                      <option value="professional">Professional</option>
                      <option value="casual">Casual</option>
                      <option value="authoritative">Authoritative</option>
                      <option value="friendly">Friendly</option>
                      <option value="innovative">Innovative</option>
                    </Select>
                  </FormControl>

                  {/* Custom Instructions */}
                  <FormControl>
                    <FormLabel>Custom Instructions</FormLabel>
                    <Textarea
                      placeholder="Any specific requirements or style guidelines"
                      value={customInstructions}
                      onChange={(e) => setCustomInstructions(e.target.value)}
                      rows={3}
                    />
                  </FormControl>
                </VStack>
              </GridItem>

              <GridItem>
                <VStack spacing={6} align="stretch">
                  {/* Image Upload */}
                  <FormControl>
                    <FormLabel>Visual Context Image (Optional)</FormLabel>
                    <Box
                      border="2px dashed"
                      borderColor={selectedImage ? "green.300" : "gray.300"}
                      borderRadius="md"
                      p={6}
                      textAlign="center"
                      cursor="pointer"
                      onClick={() => document.getElementById('image-upload').click()}
                      _hover={{ borderColor: "blue.400" }}
                    >
                      {imagePreview ? (
                        <VStack spacing={4}>
                          <Image 
                            src={imagePreview} 
                            maxH="200px" 
                            objectFit="cover" 
                            borderRadius="md"
                            onClick={onImageModalOpen}
                          />
                          <Button 
                            size="sm" 
                            variant="outline" 
                            leftIcon={<FiEye />}
                            onClick={(e) => {
                              e.stopPropagation();
                              onImageModalOpen();
                            }}
                          >
                            View Full Size
                          </Button>
                        </VStack>
                      ) : (
                        <VStack spacing={3}>
                          <Icon as={FiImage} boxSize={8} color="gray.400" />
                          <Text color="gray.600">
                            Click to upload an image for visual context analysis
                          </Text>
                          <Text fontSize="sm" color="gray.500">
                            JPG, PNG up to 10MB
                          </Text>
                        </VStack>
                      )}
                      <input
                        id="image-upload"
                        type="file"
                        accept="image/*"
                        onChange={handleImageSelect}
                        style={{ display: 'none' }}
                      />
                    </Box>
                  </FormControl>

                  {/* Campaign Overview */}
                  {campaign && (
                    <Box p={4} bg="blue.50" borderRadius="md">
                      <Heading size="md" mb={3}>Campaign Overview</Heading>
                      <VStack align="stretch" spacing={2}>
                        <HStack justify="space-between">
                          <Text fontSize="sm">Topic:</Text>
                          <Text fontSize="sm" fontWeight="bold">{campaign.topic}</Text>
                        </HStack>
                        <HStack justify="space-between">
                          <Text fontSize="sm">Consistency Score:</Text>
                          <Badge colorScheme={campaign.consistency_score > 0.8 ? 'green' : 'yellow'}>
                            {Math.round(campaign.consistency_score * 100)}%
                          </Badge>
                        </HStack>
                        <HStack justify="space-between">
                          <Text fontSize="sm">Platforms:</Text>
                          <Text fontSize="sm">3 (Twitter, LinkedIn, Podcast)</Text>
                        </HStack>
                      </VStack>
                    </Box>
                  )}

                  {/* Generate Button */}
                  <Button
                    size="lg"
                    colorScheme="blue"
                    leftIcon={isGenerating ? <FiRefreshCw /> : <FiZap />}
                    onClick={generateCampaign}
                    isLoading={isGenerating}
                    loadingText="Generating Campaign..."
                    isDisabled={!topic.trim()}
                  >
                    Generate Campaign
                  </Button>
                </VStack>
              </GridItem>
            </Grid>
          </CardBody>
        </Card>

        {/* Results Section */}
        {campaign && (
          <>
            {/* Analytics Overview */}
            {analytics && (
              <Card>
                <CardHeader>
                  <Heading size="lg">Campaign Analytics</Heading>
                </CardHeader>
                <CardBody>
                  <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6}>
                    <Stat textAlign="center">
                      <StatLabel>Overall Consistency</StatLabel>
                      <StatNumber color="green.500">
                        {Math.round(campaign.consistency_score * 100)}%
                      </StatNumber>
                      <StatHelpText>Content Alignment Score</StatHelpText>
                    </Stat>
                    <Stat textAlign="center">
                      <StatLabel>Estimated Reach</StatLabel>
                      <StatNumber color="blue.500">3.5K-7.5K</StatNumber>
                      <StatHelpText>Combined Platform Reach</StatHelpText>
                    </Stat>
                    <Stat textAlign="center">
                      <StatLabel>Engagement Rate</StatLabel>
                      <StatNumber color="purple.500">3.8%</StatNumber>
                      <StatHelpText>Projected Average</StatHelpText>
                    </Stat>
                  </Grid>

                  <Divider my={6} />

                  <Box>
                    <Text fontWeight="bold" mb={3}>Optimization Suggestions:</Text>
                    <VStack align="stretch" spacing={2}>
                      {analytics.optimization_suggestions.map((suggestion, index) => (
                        <Alert key={index} status="info" variant="left-accent">
                          <AlertIcon />
                          <AlertDescription fontSize="sm">
                            {suggestion}
                          </AlertDescription>
                        </Alert>
                      ))}
                    </VStack>
                  </Box>
                </CardBody>
              </Card>
            )}

            {/* Content Generation Progress */}
            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Campaign Generated Successfully!</AlertTitle>
                <AlertDescription>
                  Your cross-platform content campaign is ready with consistent messaging across all three platforms.
                </AlertDescription>
              </Box>
            </Alert>

            {/* Content Pieces */}
            <VStack spacing={6} align="stretch">
              <Heading size="lg">Generated Content</Heading>
              
              {/* Platform Tabs */}
              <PlatformTabs />

              {/* Full Content Grid */}
              <Grid templateColumns={{ base: '1fr', lg: 'repeat(3, 1fr)' }} gap={6}>
                {campaign.content_pieces.map((piece) => (
                  <ContentPiece 
                    key={piece.platform}
                    piece={piece}
                    platform={piece.platform}
                    icon={piece.platform === 'twitter' ? FiTwitter : 
                         piece.platform === 'linkedin' ? FiLinkedin : FiMic}
                  />
                ))}
              </Grid>
            </VStack>

            {/* Visual Context Analysis */}
            {campaign.visual_context && (
              <Card>
                <CardHeader>
                  <Heading size="lg">Visual Context Analysis</Heading>
                  <Text color="gray.600">AI analysis of your uploaded image</Text>
                </CardHeader>
                <CardBody>
                  <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
                    <VStack align="stretch" spacing={4}>
                      <Box>
                        <Text fontWeight="bold" mb={2}>Image Properties:</Text>
                        <VStack align="stretch" spacing={1}>
                          {campaign.visual_context.dimensions && (
                            <Text fontSize="sm">
                              Dimensions: {campaign.visual_context.dimensions.width} × {campaign.visual_context.dimensions.height}
                            </Text>
                          )}
                          {campaign.visual_context.aspect_ratio && (
                            <Text fontSize="sm">
                              Aspect Ratio: {campaign.visual_context.aspect_ratio}
                            </Text>
                          )}
                          <Text fontSize="sm">
                            Size Category: {campaign.visual_context.size_category}
                          </Text>
                        </VStack>
                      </Box>

                      <Box>
                        <Text fontWeight="bold" mb={2}>Mood Indicators:</Text>
                        <Wrap>
                          {campaign.visual_context.mood_indicators?.map((mood, index) => (
                            <WrapItem key={index}>
                              <Tag colorScheme="blue" size="sm">
                                <TagLabel>{mood}</TagLabel>
                              </Tag>
                            </WrapItem>
                          ))}
                        </Wrap>
                      </Box>
                    </VStack>

                    <VStack align="stretch" spacing={4}>
                      <Box>
                        <Text fontWeight="bold" mb={2}>Visual Elements:</Text>
                        <Wrap>
                          {campaign.visual_context.visual_elements?.map((element, index) => (
                            <WrapItem key={index}>
                              <Tag colorScheme="green" size="sm">
                                <TagLabel>{element}</TagLabel>
                              </Tag>
                            </WrapItem>
                          ))}
                        </Wrap>
                      </Box>

                      <Box>
                        <Text fontWeight="bold" mb={2}>Content Strategy:</Text>
                        <Text fontSize="sm" color="gray.600">
                          {campaign.visual_context.content_angle}
                        </Text>
                      </Box>

                      <Box>
                        <Text fontWeight="bold" mb={2}>Brand Compatibility:</Text>
                        <Badge 
                          colorScheme={campaign.visual_context.brand_compatibility === 'high' ? 'green' : 'yellow'}
                          size="lg"
                        >
                          {campaign.visual_context.brand_compatibility}
                        </Badge>
                      </Box>
                    </VStack>
                  </Grid>
                </CardBody>
              </Card>
            )}

            {/* Campaign Actions */}
            <Card>
              <CardBody>
                <HStack spacing={4} wrap="wrap">
                  <Button 
                    leftIcon={<FiDownload />} 
                    colorScheme="blue" 
                    variant="outline"
                    onClick={() => {
                      // Export campaign as JSON
                      const dataStr = JSON.stringify(campaign, null, 2);
                      const dataBlob = new Blob([dataStr], { type: 'application/json' });
                      const url = URL.createObjectURL(dataBlob);
                      const link = document.createElement('a');
                      link.href = url;
                      link.download = `${campaign.campaign_id}_campaign.json`;
                      link.click();
                    }}
                  >
                    Export Campaign
                  </Button>
                  <Button 
                    leftIcon={<FiRefreshCw />} 
                    variant="outline"
                    onClick={() => {
                      setCampaign(null);
                      setAnalytics(null);
                    }}
                  >
                    New Campaign
                  </Button>
                </HStack>
              </CardBody>
            </Card>
          </>
        )}
      </VStack>

      {/* Image Preview Modal */}
      <Modal isOpen={isImageModalOpen} onClose={onImageModalClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Image Preview</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {imagePreview && (
              <Image 
                src={imagePreview} 
                maxH="500px" 
                mx="auto" 
                objectFit="contain" 
                borderRadius="md"
              />
            )}
          </ModalBody>
          <ModalFooter>
            <Button onClick={onImageModalClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default CrossPlatformContentOrchestrator;